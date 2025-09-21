import React, { useState } from 'react';

const PhysicsConceptLibrary = () => {
  const [selectedCategory, setSelectedCategory] = useState('kinematics');
  const [selectedConcept, setSelectedConcept] = useState(null);

  const physicsConcepts = {
    kinematics: {
      title: "Kinematics",
      description: "The study of motion without considering forces",
      concepts: {
        velocity: {
          definition: "Velocity is the rate of change of position with respect to time. It's a vector quantity with both magnitude (speed) and direction.",
          formula: "v = Δx/Δt",
          units: "m/s",
          realWorldExample: "A car moving at 60 km/h has a velocity of 16.7 m/s in the direction it's traveling.",
          commonMistakes: [
            "Confusing velocity with speed (speed is just the magnitude)",
            "Forgetting that velocity includes direction"
          ],
          visualAid: "Imagine an arrow showing both how fast and in what direction something is moving."
        },
        acceleration: {
          definition: "Acceleration is the rate of change of velocity with respect to time. It indicates how quickly an object's velocity is changing.",
          formula: "a = Δv/Δt",
          units: "m/s²",
          realWorldExample: "When you press the gas pedal in a car, you experience acceleration as the car speeds up.",
          commonMistakes: [
            "Thinking acceleration always means speeding up (it can also mean slowing down or changing direction)",
            "Confusing acceleration with velocity"
          ],
          visualAid: "Think of acceleration as how quickly the speedometer needle is moving."
        },
        displacement: {
          definition: "Displacement is the change in position of an object. It's a vector quantity that shows both distance and direction from start to finish.",
          formula: "Δx = x_final - x_initial",
          units: "m",
          realWorldExample: "If you walk 3 blocks north, your displacement is 3 blocks north, regardless of the path you took.",
          commonMistakes: [
            "Confusing displacement with distance (distance is the total path length)",
            "Forgetting that displacement can be negative"
          ],
          visualAid: "Displacement is like drawing a straight line from where you started to where you ended up."
        }
      }
    },
    dynamics: {
      title: "Dynamics",
      description: "The study of forces and their effects on motion",
      concepts: {
        force: {
          definition: "Force is any interaction that changes the motion of an object. Newton's second law states F = ma.",
          formula: "F = ma",
          units: "N (Newtons)",
          realWorldExample: "When you push a shopping cart, you apply a force that makes it move.",
          commonMistakes: [
            "Thinking a force is needed to keep an object moving (Newton's first law says otherwise)",
            "Confusing force with energy"
          ],
          visualAid: "Forces are like invisible pushes or pulls that change how objects move."
        },
        momentum: {
          definition: "Momentum is the product of an object's mass and velocity. It's conserved in isolated systems.",
          formula: "p = mv",
          units: "kg⋅m/s",
          realWorldExample: "A heavy truck has more momentum than a bicycle at the same speed.",
          commonMistakes: [
            "Thinking momentum and velocity are the same thing",
            "Forgetting that momentum depends on both mass and velocity"
          ],
          visualAid: "Momentum is like the 'oomph' an object has - bigger, faster objects have more momentum."
        },
        friction: {
          definition: "Friction is a force that opposes motion between two surfaces in contact.",
          formula: "f = μN (where μ is coefficient of friction, N is normal force)",
          units: "N (Newtons)",
          realWorldExample: "Friction between your shoes and the ground allows you to walk without slipping.",
          commonMistakes: [
            "Thinking friction is always bad (it's often necessary for motion)",
            "Confusing static and kinetic friction"
          ],
          visualAid: "Friction is like tiny bumps on surfaces that catch and slow down motion."
        }
      }
    },
    energy: {
      title: "Energy",
      description: "The capacity to do work or cause change",
      concepts: {
        kinetic_energy: {
          definition: "Kinetic energy is the energy an object possesses due to its motion.",
          formula: "KE = ½mv²",
          units: "J (Joules)",
          realWorldExample: "A moving baseball has kinetic energy that can break a window.",
          commonMistakes: [
            "Thinking kinetic energy depends only on speed (it also depends on mass)",
            "Confusing kinetic energy with momentum"
          ],
          visualAid: "Kinetic energy is like the 'energy of motion' - faster objects have much more kinetic energy."
        },
        potential_energy: {
          definition: "Potential energy is stored energy due to an object's position or configuration.",
          formula: "PE = mgh (gravitational potential energy)",
          units: "J (Joules)",
          realWorldExample: "A book on a high shelf has gravitational potential energy.",
          commonMistakes: [
            "Thinking potential energy is always gravitational",
            "Forgetting that potential energy depends on the reference point"
          ],
          visualAid: "Potential energy is like stored energy waiting to be released, like a stretched rubber band."
        },
        conservation_of_energy: {
          definition: "Energy cannot be created or destroyed, only transformed from one form to another.",
          formula: "E_initial = E_final (in isolated systems)",
          units: "J (Joules)",
          realWorldExample: "A roller coaster converts potential energy to kinetic energy as it goes down hills.",
          commonMistakes: [
            "Thinking energy can be lost (it's just transformed)",
            "Forgetting to account for all forms of energy"
          ],
          visualAid: "Energy is like water - it can change form (ice, liquid, vapor) but the total amount stays the same."
        }
      }
    }
  };

  const categories = Object.keys(physicsConcepts);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
        📚 Physics Concept Library
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Selection */}
        <div className="lg:col-span-1">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Categories</h3>
          <div className="space-y-2">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => {
                  setSelectedCategory(category);
                  setSelectedConcept(null);
                }}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedCategory === category
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <div className="font-medium">{physicsConcepts[category].title}</div>
                <div className="text-sm opacity-75">{physicsConcepts[category].description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Concept List */}
        <div className="lg:col-span-1">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Concepts</h3>
          <div className="space-y-2">
            {Object.keys(physicsConcepts[selectedCategory].concepts).map((conceptKey) => (
              <button
                key={conceptKey}
                onClick={() => setSelectedConcept(conceptKey)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedConcept === conceptKey
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <div className="font-medium capitalize">
                  {conceptKey.replace('_', ' ')}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Concept Details */}
        <div className="lg:col-span-1">
          {selectedConcept ? (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4 capitalize">
                {selectedConcept.replace('_', ' ')}
              </h3>
              {(() => {
                const concept = physicsConcepts[selectedCategory].concepts[selectedConcept];
                return (
                  <div className="space-y-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-blue-800 mb-2">Definition</h4>
                      <p className="text-blue-700">{concept.definition}</p>
                    </div>

                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-green-800 mb-2">Formula</h4>
                      <div className="bg-white p-3 rounded border font-mono text-green-700">
                        {concept.formula}
                      </div>
                      <p className="text-green-600 text-sm mt-2">Units: {concept.units}</p>
                    </div>

                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-yellow-800 mb-2">Real-World Example</h4>
                      <p className="text-yellow-700">{concept.realWorldExample}</p>
                    </div>

                    <div className="bg-purple-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-purple-800 mb-2">Visual Aid</h4>
                      <p className="text-purple-700">{concept.visualAid}</p>
                    </div>

                    <div className="bg-red-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-red-800 mb-2">Common Mistakes</h4>
                      <ul className="space-y-1">
                        {concept.commonMistakes.map((mistake, index) => (
                          <li key={index} className="text-red-700 text-sm">• {mistake}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                );
              })()}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              Select a concept to see details
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PhysicsConceptLibrary;
