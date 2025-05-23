import numpy as np
import pickle

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        # Initialiser les poids et biais avec des valeurs aléatoires
        self.weights_input_hidden = np.random.rand(input_size, hidden_size)
        self.bias_hidden = np.random.rand(1, hidden_size)

        self.weights_hidden_output = np.random.rand(hidden_size, output_size)
        self.bias_output = np.random.rand(1, output_size)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def train(self, inputs, targets, epochs=10000, learning_rate=0.1):
        for epoch in range(epochs):
            # Avant
            hidden_layer_input = np.dot(inputs, self.weights_input_hidden) + self.bias_hidden
            hidden_layer_output = self.sigmoid(hidden_layer_input)

            output_layer_input = np.dot(hidden_layer_output, self.weights_hidden_output) + self.bias_output
            predicted_output = self.sigmoid(output_layer_input)

            # Erreur
            error = targets - predicted_output

            # Calcule le gradient
            d_predicted_output = error * self.sigmoid_derivative(predicted_output)
            error_hidden_layer = d_predicted_output.dot(self.weights_hidden_output.T)
            d_hidden_layer = error_hidden_layer * self.sigmoid_derivative(hidden_layer_output)

            # Met à jour les poids et biais
            self.weights_hidden_output += hidden_layer_output.T.dot(d_predicted_output) * learning_rate
            self.bias_output += np.sum(d_predicted_output, axis=0, keepdims=True) * learning_rate

            self.weights_input_hidden += inputs.T.dot(d_hidden_layer) * learning_rate
            self.bias_hidden += np.sum(d_hidden_layer, axis=0, keepdims=True) * learning_rate

    def predict(self, inputs):
        hidden_layer_input = np.dot(inputs, self.weights_input_hidden) + self.bias_hidden
        hidden_layer_output = self.sigmoid(hidden_layer_input)

        output_layer_input = np.dot(hidden_layer_output, self.weights_hidden_output) + self.bias_output
        predicted_output = self.sigmoid(output_layer_input)
        return predicted_output

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump({
                "weights_input_hidden": self.weights_input_hidden,
                "bias_hidden": self.bias_hidden,
                "weights_hidden_output": self.weights_hidden_output,
                "bias_output": self.bias_output
            }, f)

    def load(self, filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            self.weights_input_hidden = data["weights_input_hidden"]
            self.bias_hidden = data["bias_hidden"]
            self.weights_hidden_output = data["weights_hidden_output"]
            self.bias_output = data["bias_output"]
