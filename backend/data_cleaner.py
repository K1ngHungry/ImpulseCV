import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

class DataCleaner:
    """
    Advanced outlier detection and data cleaning for object tracking data.
    Based on robust statistical methods and trajectory analysis.
    """
    
    def __init__(self, 
                 max_gap=1,           # contiguous-frame definition
                 k_speed=4.0,         # speed MAD multiplier (teleport threshold)
                 k_back=3.5,          # back-jump MAD multiplier (large negative dx)
                 back_min=15.0,       # px; minimum magnitude to consider a back-jump
                 cx_tol=8.0,          # px; allow small non-monotone wiggles in cx
                 k_resid=3.5,         # residual MAD multiplier (iterative trimming)
                 trim_passes=3,       # number of iterative trimming passes
                 invert=False):       # set True to flip inliers/outliers
        self.max_gap = max_gap
        self.k_speed = k_speed
        self.k_back = k_back
        self.back_min = back_min
        self.cx_tol = cx_tol
        self.k_resid = k_resid
        self.trim_passes = trim_passes
        self.invert = invert
    
    def mad_sigma(self, v):
        """Calculate robust standard deviation using Median Absolute Deviation"""
        v = np.asarray(v)
        v = v[np.isfinite(v)]
        if v.size == 0: 
            return 1.0
        med = np.median(v)
        mad = np.median(np.abs(v - med))
        return 1.4826 * mad if mad > 0 else (np.std(v) if v.size > 1 else 1.0)
    
    def longest_contiguous_segment(self, frames, max_gap=1):
        """Find the longest contiguous segment of frames"""
        gaps = np.diff(frames)
        brk = np.where(gaps > max_gap)[0] + 1
        starts = np.r_[0, brk]
        ends = np.r_[brk, len(frames)]
        i = np.argmax(ends - starts)
        return starts[i], ends[i]   # half-open [s,e)
    
    def clean_tracking_data(self, df, target_track=None):
        """
        Clean tracking data by removing outliers and noise.
        
        Args:
            df: DataFrame with columns ['frame', 'track_id', 'cx', 'cy', ...]
            target_track: specific track ID to clean, or None for all tracks
            
        Returns:
            cleaned_df: DataFrame with outliers removed
            cleaning_stats: dict with cleaning statistics
        """
        if len(df) < 3:
            return df, {"error": "Not enough data points for cleaning"}
        
        # Filter by target track if specified
        if target_track is not None:
            df = df[df['track_id'] == target_track].copy()
            if len(df) < 3:
                return df, {"error": f"Not enough data points for track {target_track}"}
        
        # Extract basic data
        frames = df['frame'].values.astype(int)
        cx_all = df['cx'].values
        cy_all = df['cy'].values
        
        # Collapse duplicate frames by median
        uniq = np.unique(frames)
        cx_med = np.array([np.median(cx_all[frames == f]) for f in uniq])
        cy_med = np.array([np.median(cy_all[frames == f]) for f in uniq])
        frames, cx_all, cy_all = uniq, cx_med, cy_med
        
        if len(frames) < 3:
            return df, {"error": "Not enough points after filtering/grouping"}
        
        # Keep longest contiguous run
        s, e = self.longest_contiguous_segment(frames, self.max_gap)
        frames = frames[s:e]
        cx = cx_all[s:e]
        cy = cy_all[s:e]
        n = len(frames)
        
        # Timeline-based pruning
        dx = np.diff(cx)
        dy = np.diff(cy)
        speed = np.hypot(dx, dy)
        
        thr_speed = np.median(speed) + self.k_speed * self.mad_sigma(speed)
        thr_back = max(self.back_min, self.k_back * self.mad_sigma(dx))
        
        keep = np.ones(n, dtype=bool)
        
        # (A) Teleport speeds: mark point i if adjacent speed is huge
        for i in range(n):
            if (i-1 >= 0 and speed[i-1] > thr_speed) or (i < n-1 and speed[i] > thr_speed):
                keep[i] = False
        
        # (B) Back-jumps in cx: if dx[i] is very negative, drop the later point (i+1)
        for i in range(n-1):
            if dx[i] < -thr_back:
                keep[i+1] = False
        
        # (C) Near-monotone cx with tolerance
        run_max = -np.inf
        for i in range(n):
            if cx[i] + self.cx_tol < run_max:
                keep[i] = False
            else:
                run_max = max(run_max, cx[i])
        
        # Seed cleaned arrays
        cx_cln = cx[keep]
        cy_cln = cy[keep]
        if len(cx_cln) < 3:
            cx_cln, cy_cln = cx.copy(), cy.copy()
        
        # Iterative residual trimming (robust quadratic)
        coef = np.polyfit(cx_cln, cy_cln, 2)
        for _ in range(self.trim_passes):
            yhat = np.polyval(coef, cx_cln)
            res = cy_cln - yhat
            sig = self.mad_sigma(res)
            thr_res = max(3.0, self.k_resid * sig)
            mask = np.abs(res) <= thr_res
            if mask.sum() < 3 or mask.all():
                break
            cx_cln, cy_cln = cx_cln[mask], cy_cln[mask]
            coef = np.polyfit(cx_cln, cy_cln, 2)
        
        # Build keep_full over the segment
        cln_set = set(map(tuple, np.round(np.column_stack([cx_cln, cy_cln]), 6)))
        keep_full = np.array([(round(cx[i], 6), round(cy[i], 6)) in cln_set for i in range(n)])
        
        # Optionally invert inliers/outliers
        final_inliers = ~keep_full if self.invert else keep_full
        final_outliers = ~final_inliers
        
        # Create cleaned DataFrame
        cleaned_indices = []
        for i, frame in enumerate(frames):
            if final_inliers[i]:
                # Find original row(s) for this frame
                original_rows = df[df['frame'] == frame]
                if len(original_rows) > 0:
                    # Take the first row (or could take median)
                    cleaned_indices.append(original_rows.index[0])
        
        cleaned_df = df.loc[cleaned_indices].copy() if cleaned_indices else df.copy()
        
        # Calculate cleaning statistics
        stats = {
            "original_points": len(df),
            "cleaned_points": len(cleaned_df),
            "outliers_removed": len(df) - len(cleaned_df),
            "cleaning_percentage": (len(df) - len(cleaned_df)) / len(df) * 100 if len(df) > 0 else 0,
            "speed_threshold": thr_speed,
            "back_jump_threshold": thr_back,
            "quadratic_coefficients": coef.tolist() if len(cx_cln) >= 3 else None
        }
        
        # Calculate R² if we have enough points
        if len(cx_cln) >= 3 and np.unique(cx_cln).size >= 3:
            yhat_fit = np.polyval(coef, cx_cln)
            ss_res = np.sum((cy_cln - yhat_fit)**2)
            ss_tot = np.sum((cy_cln - cy_cln.mean())**2)
            r2 = 1.0 - ss_res/ss_tot if ss_tot > 0 else 1.0
            stats["r_squared"] = r2
        
        return cleaned_df, stats
    
    def clean_all_tracks(self, df):
        """
        Clean all tracks in the DataFrame separately.
        
        Args:
            df: DataFrame with tracking data
            
        Returns:
            cleaned_df: DataFrame with all tracks cleaned
            cleaning_stats: dict with statistics for each track
        """
        if 'track_id' not in df.columns:
            return self.clean_tracking_data(df)
        
        all_cleaned = []
        all_stats = {}
        
        for track_id in df['track_id'].unique():
            track_df = df[df['track_id'] == track_id].copy()
            cleaned_track, stats = self.clean_tracking_data(track_df, target_track=track_id)
            all_cleaned.append(cleaned_track)
            all_stats[f"track_{track_id}"] = stats
        
        if all_cleaned:
            final_df = pd.concat(all_cleaned, ignore_index=True)
            final_df = final_df.sort_values(['track_id', 'frame']).reset_index(drop=True)
        else:
            final_df = df.copy()
        
        return final_df, all_stats
    
    def plot_cleaning_results(self, df, cleaned_df, output_path=None):
        """
        Create a visualization of the cleaning results.
        
        Args:
            df: original DataFrame
            cleaned_df: cleaned DataFrame
            output_path: path to save the plot (optional)
        """
        plt.figure(figsize=(12, 8))
        
        # Plot original data
        plt.scatter(df['cx'], df['cy'], s=10, c='0.85', 
                   label=f"Original data (n={len(df)})", alpha=0.6, zorder=1)
        
        # Plot cleaned data
        plt.scatter(cleaned_df['cx'], cleaned_df['cy'], s=20,
                   facecolors='none', edgecolors='tab:blue', linewidths=1.0,
                   label=f"Cleaned data (n={len(cleaned_df)})", zorder=3)
        
        # Plot outliers
        outliers = df[~df.index.isin(cleaned_df.index)]
        if len(outliers) > 0:
            plt.scatter(outliers['cx'], outliers['cy'], s=20,
                       facecolors='none', edgecolors='tab:red', linewidths=1.0,
                       label=f"Outliers removed (n={len(outliers)})", zorder=2)
        
        plt.gca().set_aspect('equal', adjustable='datalim')
        plt.xlabel("cx (pixels)")
        plt.ylabel("cy (pixels)")
        plt.title("Data Cleaning Results")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Cleaning visualization saved to: {output_path}")
        
        return plt.gcf()
