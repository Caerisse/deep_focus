import torch
from progressbar import progressbar
from torch.nn.parameter import Parameter
from torch.nn import functional
from torch.nn import init
from torch.nn.modules import Module
import torch.optim as optim
import torch.utils.data
import numpy as np

class DeepFocusNALU:
    def __init__(self, calibration_data):
        inputs  = np.array([np.array(calibration_data_line[0]) for calibration_data_line in calibration_data])
        outputs = np.array([np.array(calibration_data_line[1]) for calibration_data_line in calibration_data])

        dataset = torch.utils.data.TensorDataset(torch.Tensor(inputs), torch.Tensor(outputs))
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=512, shuffle=True, num_workers=0)

        self.model = NALU(14, 2)#.cuda()
        opt = optim.Adam(self.model.parameters(), 1e-2)
        crit = functional.mse_loss
        self.fit(self.model, dataloader, opt, crit)

    def fit(self, m, dataloader, opt, crit):
        print("Starting training")
        for epoch in progressbar(range(100)):  # loop over the dataset multiple times
            running_loss = 0.0
            for i, data in enumerate(dataloader):
                # get the inputs
                inputs, labels = data
                inputs = inputs.float()  # .cuda().float()
                labels = labels.float()  # .cuda().float()

                # zero the parameter gradients
                opt.zero_grad()

                # forward + backward + optimize
                outputs = m(inputs)
                loss = crit(outputs, labels)
                loss.backward()
                opt.step()

                # print statistics
                running_loss += loss.item()
                if i % 8 == 7 and epoch % 20 == 19: # Print every eight minibatch of every 20th epoch
                    print('[%d] loss: %.3f' % (epoch + 1, running_loss / 8))
                    running_loss = 0.0

class NAC(Module):
    def __init__(self, n_in, n_out):
        super().__init__()
        self.W_hat = Parameter(torch.Tensor(n_out, n_in))
        self.M_hat = Parameter(torch.Tensor(n_out, n_in))
        self.reset_parameters()

    def reset_parameters(self):
        init.kaiming_uniform_(self.W_hat)
        init.kaiming_uniform_(self.M_hat)

    def forward(self, input):
        weights = torch.tanh(self.W_hat) * torch.sigmoid(self.M_hat)
        return functional.linear(input, weights)


class NALU(Module):
    def __init__(self, n_in, n_out):
        super().__init__()
        self.NAC = NAC(n_in, n_out)
        self.G = Parameter(torch.Tensor(1, n_in))
        self.eps = 1e-6
        self.reset_parameters()

    def reset_parameters(self):
        init.kaiming_uniform_(self.G)

    def forward(self, input):
        g = torch.sigmoid(functional.linear(input, self.G))
        y1 = g * self.NAC(input)
        y2 = (1 - g) * torch.exp(self.NAC(torch.log(torch.abs(input) + self.eps)))
        return y1 + y2