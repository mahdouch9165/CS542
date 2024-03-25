import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.metrics import explained_variance_score
import plotly.graph_objects as go
from torch import Tensor
import numpy as np
from typing import Optional, Tuple
import torch.nn.functional as F
from torch.optim.lr_scheduler import ReduceLROnPlateau
import joblib

# Define the LSTM model
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout_rate=0.2):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.dropout1 = nn.Dropout(dropout_rate)
        self.fc1 = nn.Linear(hidden_size, 128)
        self.dropout2 = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(128, output_size)
        self.layer_norm1 = nn.LayerNorm(hidden_size)
        self.layer_norm2 = nn.LayerNorm(128)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        out = self.dropout1(out[:, -1, :])
        out = self.layer_norm1(out)
        out = torch.relu(self.fc1(out))
        out = self.dropout2(out)
        out = self.layer_norm2(out)
        out = self.fc2(out)
        return out

class SimpleLSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(SimpleLSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out
    
class ScaledDotProductAttention(nn.Module):
    """
    Scaled Dot-Product Attention proposed in "Attention Is All You Need"
    Compute the dot products of the query with all keys, divide each by sqrt(dim),
    and apply a softmax function to obtain the weights on the values

    Args: dim, mask
        dim (int): dimention of attention
        mask (torch.Tensor): tensor containing indices to be masked

    Inputs: query, key, value, mask
        - **query** (batch, q_len, d_model): tensor containing projection vector for decoder.
        - **key** (batch, k_len, d_model): tensor containing projection vector for encoder.
        - **value** (batch, v_len, d_model): tensor containing features of the encoded input sequence.
        - **mask** (-): tensor containing indices to be masked

    Returns: context, attn
        - **context**: tensor containing the context vector from attention mechanism.
        - **attn**: tensor containing the attention (alignment) from the encoder outputs.
    """
    def __init__(self, dim: int):
        super(ScaledDotProductAttention, self).__init__()
        self.sqrt_dim = np.sqrt(dim)

    def forward(self, query: Tensor, key: Tensor, value: Tensor, mask: Optional[Tensor] = None) -> Tuple[Tensor, Tensor]:
        score = torch.bmm(query, key.transpose(1, 2)) / self.sqrt_dim

        if mask is not None:
            score.masked_fill_(mask.view(score.size()), -float('Inf'))

        attn = F.softmax(score, -1)
        context = torch.bmm(attn, value)
        return context, attn

class AttentionLSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout_rate=0.3):
        super(AttentionLSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.attention = ScaledDotProductAttention(hidden_size)
        self.dropout1 = nn.Dropout(dropout_rate)
        self.fc1 = nn.Linear(hidden_size, 128)
        self.dropout2 = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(128, 64)
        self.dropout3 = nn.Dropout(dropout_rate)
        self.fc3 = nn.Linear(64, output_size)
        self.layer_norm1 = nn.LayerNorm(hidden_size)
        self.layer_norm2 = nn.LayerNorm(128)
        self.layer_norm3 = nn.LayerNorm(64)

    def forward(self, x, mask=None):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        out, (h_n, c_n) = self.lstm(x, (h0, c0))
        
        # Apply attention to LSTM output
        query = out[:, -1, :].unsqueeze(1)  # Use the last hidden state of each time step as the query
        context, attn = self.attention(query, out, out, mask)
        out = self.dropout1(context.squeeze(1))
        out = self.layer_norm1(out)
        
        # Apply attention to the first fully connected layer
        query = out.unsqueeze(1)
        context, attn = self.attention(query, out.unsqueeze(1), out.unsqueeze(1), mask)
        out = torch.relu(self.fc1(context.squeeze(1)))
        out = self.dropout2(out)
        out = self.layer_norm2(out)
        
        # Apply attention to the second fully connected layer
        query = out.unsqueeze(1)
        context, attn = self.attention(query, out.unsqueeze(1), out.unsqueeze(1), mask)
        out = torch.relu(self.fc2(context.squeeze(1)))
        out = self.dropout3(out)
        out = self.layer_norm3(out)
        
        out = self.fc3(out)
        return out

def train_model(model, X_train, y_train, X_val, y_val, l2_lambda=0.1, epochs = 20, lr=  0.001):
    criterion = nn.MSELoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=5, verbose=True)


    # Train the model
    num_epochs = epochs
    batch_size = 32
    loss_history = []
    val_loss_history = []

    for epoch in range(num_epochs):
        epoch_loss = 0.0
        num_batches = 0
        
        for i in range(0, len(X_train), batch_size):
            inputs = X_train[i:i+batch_size]
            targets = y_train[i:i+batch_size]
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets.view(-1, 1))
            
            l2_reg = torch.tensor(0.)
            for param in model.parameters():
                l2_reg += torch.norm(param)
            loss += l2_lambda * l2_reg
            
            epoch_loss += loss.item()
            num_batches += 1
            
            loss.backward()
            optimizer.step()
        
        # Calculate average training loss for the epoch
        avg_epoch_loss = epoch_loss / num_batches
        loss_history.append(avg_epoch_loss)
        
        # Evaluate the model on the validation set
        with torch.no_grad():
            val_outputs = model(X_val)
            val_loss = criterion(val_outputs, y_val.view(-1, 1))
            val_loss_history.append(val_loss.item())
            
        scheduler.step(val_loss)
        
        print(f'Epoch [{epoch+1}/{num_epochs}], Train Loss: {avg_epoch_loss:.4f}, Val Loss: {val_loss.item():.4f}')
        
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, num_epochs+1), loss_history, label='Training Loss')
    plt.plot(range(1, num_epochs+1), val_loss_history, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()
    return model

def get_model(X_train, y_train, dropout_rate=0.2, hidden_size=64, num_layers=1, model_type='lstm'):
    input_size = X_train.shape[2]
    hidden_size = hidden_size
    num_layers = num_layers
    output_size = 1
    if model_type == 'lstm':
        model = LSTMModel(input_size, hidden_size, num_layers, output_size, dropout_rate=dropout_rate)
    elif model_type == 'attn_lstm':
        model = AttentionLSTMModel(input_size, hidden_size, num_layers, output_size, dropout_rate=dropout_rate)
    return model

def get_test_loss(model, X_test, y_test):
    criterion = nn.MSELoss()
    with torch.no_grad():
        test_outputs = model(X_test)
        test_loss = criterion(test_outputs, y_test.view(-1, 1))
    print(f'Test Loss: {test_loss:.4f}')
    return test_loss.item()

def plot_preds(test_outputs, y_test):
    y_pred = test_outputs.detach().numpy()[:, -1]
    y_true = y_test.numpy()

    print(f'Explained Variance Score: {explained_variance_score(y_true, y_pred):.4f}')

    # Print mean squared error on the test data
    mse = np.mean((y_pred - y_true) ** 2)
    print(f'Mean Squared Error: {mse:.4f}')

    # mae
    mae = np.mean(np.abs(y_pred - y_true))
    print(f'Mean Absolute Error: {mae:.4f}')

    # std error
    std_error = np.std(y_pred - y_true)
    print(f'Standard Error: {std_error:.4f}')

    confidence_interval = 1.96 * std_error
    print(f'95% Confidence Interval: {confidence_interval:.4f}')

    # Plot the predicted and true values
    upper_bound = y_pred + confidence_interval
    lower_bound = y_pred - confidence_interval

    trace_actual = go.Scatter(
        x=np.arange(len(y_true)),
        y=y_true,
        mode='lines',
        name='Actual'
    )

    trace_predicted = go.Scatter(
        x=np.arange(len(y_pred)),
        y=y_pred,
        mode='lines',
        name='Predicted'
    )

    # Create traces for the uncertainty shading
    trace_upper_bound = go.Scatter(
        x=np.arange(len(y_pred)),
        y=upper_bound,
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        showlegend=False
    )

    trace_lower_bound = go.Scatter(
        x=np.arange(len(y_pred)),
        y=lower_bound,
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty',
        showlegend=False
    )

    # Create the layout for the figure
    layout = go.Layout(
        title='Predicted vs. Actual Values with 95% Confidence Interval',
        xaxis=dict(title='Data Points'),
        yaxis=dict(title='Values')
    )

    # Create the figure
    fig = go.Figure(data=[trace_actual, trace_predicted, trace_upper_bound, trace_lower_bound], layout=layout)

    # Display the figure
    fig.show()

def weight_transfer(model2, model):
    input_size = model.lstm.input_size
    input_size_data2 = model2.lstm.input_size
    
    hidden_size = model.lstm.hidden_size
    
    model1_state_dict = model.state_dict()
    model2_state_dict = model2.state_dict()

    # Transfer weights for the common layers
    for name, param in model1_state_dict.items():
        if name in model2_state_dict:
            if param.size() == model2_state_dict[name].size():
                model2_state_dict[name].copy_(param)
            else:
                if name == 'lstm.weight_ih_l0':
                    # Initialize the additional input weights randomly
                    additional_input_size = input_size_data2 - input_size
                    model2_state_dict[name][:, :input_size] = param
                    model2_state_dict[name][:, input_size:] = torch.randn(hidden_size * 4, additional_input_size)
                else:
                    print(f"Size mismatch for {name}: {param.size()} vs {model2_state_dict[name].size()}")

    model2.load_state_dict(model2_state_dict)
    
    return model2

def prep_data(data, columns_to_ignore, target_column):
    # Prepare the data for LSTM
    features = data.drop(columns=columns_to_ignore).columns
    target = target_column

    # Split the data into training, validation, and testing sets
    train_size = int(len(data) * 0.7)
    val_size = int(len(data) * 0.15)
    train_data = data[:train_size]
    val_data = data[train_size:train_size+val_size]
    test_data = data[train_size+val_size:]

    # Scale the features using only the training data
    scaler_features = StandardScaler()
    train_features = scaler_features.fit_transform(train_data[features])
    val_features = scaler_features.transform(val_data[features])
    test_features = scaler_features.transform(test_data[features])

    # Create the input sequences and corresponding labels for the LSTM model
    def create_sequences(features, target, seq_length):
        X = []
        y = []
        for i in range(len(features) - seq_length):
            X.append(features[i:i+seq_length])
            y.append(target[i+seq_length])
        return np.array(X), np.array(y)

    seq_length = 20  # Number of previous days to use as input
    X_train, y_train = create_sequences(train_features, train_data[target].values, seq_length)
    X_val, y_val = create_sequences(val_features, val_data[target].values, seq_length)
    X_test, y_test = create_sequences(test_features, test_data[target].values, seq_length)

    # Convert the data to PyTorch tensors
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32)
    X_val = torch.tensor(X_val, dtype=torch.float32)
    y_val = torch.tensor(y_val, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.float32)
    
    return X_train, y_train, X_val, y_val, X_test, y_test, scaler_features

def load_model(path):
    model = torch.load(path)
    return model

def load_xgb(path):
    model = joblib.load(path)
    return model

def load_scaler(path):
    scaler = joblib.load(path)
    return scaler