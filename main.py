import numpy as np
import NeuralNetwork

def main():
    # Entrées et sorties du problème XOR
    inputs = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    targets = np.array([[0], [1], [1], [0]])

    # Créer un réseau de neurones avec une couche cachée
    nn = NeuralNetwork(input_size=2, hidden_size=4, output_size=1)

    # Entrainer le réseau
    nn.train(inputs, targets, epochs=10000, learning_rate=0.1)

    # Sauvegarder le modèle
    nn.save("neural_network_model.pkl")

    # Charger et tester le modèle sauvegardé
    nn.load("neural_network_model.pkl")
    for i in range(len(inputs)):
        print(f"Input: {inputs[i]}, Predicted: {nn.predict(np.array([inputs[i]]))}")

if __name__ == "__main__":
    main()
  
