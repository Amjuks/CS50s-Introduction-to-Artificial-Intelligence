# CS50 AI - Traffic Project

I have tried many different combinations of layers. First I tried adding 2 pairs of convolution and 2x2 max pooling, and a hidden layer with 500 neurons. The accuracy was too low so I added two more hidden layers with 500 neurons. The accuracy decreased more after that.

I figured pooling it twice must have decreased the accuracy, so I removed one of the convolutional and pooling layers. The accuracy increased rapidly after that, but it was still less. Then I started increasing number of neurons to 1000 and 1500, and the accuracy decreased more. I realised that too many neurons made it hard to generalise weights for the network, so I changed the number of hidden layers to one and the number of hidden neurons to 250 and 500. I noticed the accuracy increasing rapidly, but it took a lot of time.

I tested adding dropouts with values `0.1`, `0.2`, and `0.4`, and noticed it didn't help much in this case so I removed them. Then I changed the number of hidden layers to one and number of neurons to 100. The accuracy and speed increased really well. I played around with the number of neurons and figured out 90 had the fastest results. I played around with activation functions and found out `sigmoid` activation worked best for this one. Now the accuracy is more than 99% and takes approximately 8 seconds on each epoch.
