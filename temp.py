# dict = {3:[1,2,3],7:[4,5,6],9:[0,0]}
# for key,value in dict.items():
#     print(key,value)
#
# import pulp
# dict = {0:[]}
# tmplist = dict[0]
# tmplist.append(5)
# dict[0]=tmplist
# for key,value in dict.items():
#     print(key,value)
#
# print(pulp.__version__)

# https://blog.csdn.net/u013398034/article/details/112789084
import torchvision.models as m
import torch.nn as nn
import torch
import torchvision.models as models

resnet50 = models.resnet50(pretrained=True)
vgg16 = models.vgg16(pretrained=True)
alexnet = models.alexnet(pretrained=True)
squeezenet = models.squeezenet1_0(pretrained=True)
vgg19 = models.vgg19(pretrained=True)

class LSTMnet(nn.Module):
    def __init__(self, in_dim, hidden_dim, n_layer, n_class):
        super(LSTMnet, self).__init__()
        self.n_layer = n_layer
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(in_dim, hidden_dim, n_layer, batch_first=True)
        self.linear = nn.Linear(hidden_dim, n_class)

    def forward(self, x):  # x‘s shape (batch_size, 序列长度, 序列中每个数据的长度)
        x = x.view(-1, 32, 32 * 3)
        out, _ = self.lstm(x)  # out‘s shape (batch_size, 序列长度, hidden_dim)
        out = out[:, -1, :]  # 中间的序列长度取-1，表示取序列中的最后一个数据，这个数据长度为hidden_dim，
        # 得到的out的shape为(batch_size, hidden_dim)
        out = self.linear(out)  # 经过线性层后，out的shape为(batch_size, n_class)
        return out


lstm = LSTMnet(32*3,1800,18,10) # 图片大小28*28，lstm的每个隐藏层56（自己设定数量大小）个节点，2层隐藏层
print(lstm)

resnet50_size = sum([param.nelement() for param in resnet50.parameters()])
vgg16_size = sum([param.nelement() for param in vgg16.parameters()])
vgg19_size = sum([param.nelement() for param in vgg19.parameters()])
alexnet_size = sum([param.nelement() for param in alexnet.parameters()])
squeezenet_size = sum([param.nelement() for param in squeezenet.parameters()])
lstm_size = sum([param.nelement() for param in lstm.parameters()])

print("Size of lstm's parameters: %.2fM" % (lstm_size/1e6))
print("Size of resnet50's parameters: %.2fM" % (resnet50_size/1e6))
# print("Size of vgg16's parameters: %.2fM" % (vgg16_size/1e6))
print("Size of vgg19's parameters: %.2fM" % (vgg19_size/1e6))
# print("Size of alexnet's parameters: %.2fM" % (alexnet_size/1e6))
# print("Size of squeezenet's parameters: %.2fM" % (squeezenet_size/1e6))