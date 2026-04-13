import torch
import torch.nn as nn
# Different NN models from torch

class RNN(nn.Module):
    """Basic RNN model for text classification."""
    def __init__(self, vocab_size, embed_dim, hidden_dim, output_dim, n_layers=1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.RNN(embed_dim, hidden_dim, num_layers=n_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, text):
        embedded = self.embedding(text)  # [batch_size, seq_len, embed_dim]
        output, hidden = self.rnn(embedded)  # output: [batch_size, seq_len, hidden_dim]
        hidden = hidden.squeeze(0)  # [batch_size, hidden_dim]
        return self.fc(hidden)

class LSTM(nn.Module):
    """RNN model designed to learn and remember information over long sequences of data. Good for text analysis."""
    def __init__(self, vocab_size, embed_dim, hidden_dim, output_dim, n_layers=1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=n_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, text):
        embedded = self.embedding(text)
        output, (hidden, cell) = self.lstm(embedded)
        hidden = hidden.squeeze(0)
        return self.fc(hidden)

class GRU(nn.Module):
    """RNN Model similar to LSTM but fewer parameters. Faster and easier to train. Potentially better for small features, not long text pieces."""
    def __init__(self, vocab_size, embed_dim, hidden_dim, output_dim, n_layers=1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.gru = nn.GRU(embed_dim, hidden_dim, num_layers=n_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, text):
        embedded = self.embedding(text)
        output, hidden = self.gru(embedded)
        hidden = hidden.squeeze(0)
        return self.fc(hidden)