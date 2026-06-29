import torch
import torch.nn as nn

class Autoencoder(nn.Module):
    def __init__(self):
        super(Autoencoder, self).__init__()
        self.encoding = nn.Sequential(
            nn.Conv3d(1, 1, 3),
            nn.MaxPool3d(2),
            nn.Sigmoid(),
            nn.Conv3d(1, 1, 3),
            nn.MaxPool3d(2),
            nn.Sigmoid()
        )
        self.decoding = nn.Sequential(
            nn.ConvTranspose3d(1, 1, 3,stride=2),
            nn.Sigmoid(),
            nn.ConvTranspose3d(1, 1, 3,stride=2),
            nn.Sigmoid(),
            nn.ConvTranspose3d(1, 1, 3),
            nn.Sigmoid(),
            nn.ConvTranspose3d(1, 1, 2),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.encoding(x)
        x = self.decoding(x)
        return x
'''
class CNN3D(nn.Module):
    def __init__(self):
        super(CNN3D, self).__init__()
        self.conv1 = nn.Conv3d(1, 1, 3,stride=(1,2,1))#cambia
        self.pool1 = nn.MaxPool3d(4)
        self.sigm1 = nn.Sigmoid()
        self.conv2 = nn.Conv3d(1, 1, 3)

        self.lin1  = nn.Linear(10*10*10,10)
        self.lin2  = nn.Linear(10,2)
        self.flatten = nn.Flatten()
    def forward(self, x):
        x = self.conv1(x)
        x = self.pool1(x)
        x = self.sigm1(x)
        x = self.conv2(x)

        x = self.flatten(x)
        x = self.lin1(x)
        x = self.lin2(x)
        return x
'''
class CNN3D(nn.Module):
    def __init__(self):
        super(CNN3D, self).__init__()        
        self.conv1 = nn.Conv3d(1, 1,kernel_size=(3,3,3),stride=(1,1,1))
        self.pool1 = nn.MaxPool3d(kernel_size=(4, 4, 4))
        self.conv2 = nn.Conv3d(1, 1, 3)
        self.sigm1 = nn.Sigmoid()

        self.lin1  = nn.Linear(2200,10)
        #self.lin1  = nn.Linear(3200,10)
        self.lin2  = nn.Linear(10,3)
        self.flatten = nn.Flatten()
    def forward(self, x):
        x = self.conv1(x)
        x = self.sigm1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.sigm1(x)
        x = self.flatten(x)
        x = self.lin1(x)
        x = self.lin2(x)

        return x
