import base64,urllib
import io

from django.db import models
import matplotlib.pyplot as plt
import numpy as np

xpoints = np.array([1, 8])
ypoints = np.array([3, 10])

plt.plot(xpoints, ypoints)
plt.show()
# Create your models here.

class plotter:
    def __init__(self):
        self.arcthickness = 0
        self.pyramidheight = 0
        self.xpoints = np.empty(0)
        self.ypoints = np.empty(0)

    def setvalues(self,arcthickness,pyramidheight):
        self.arcthickness = arcthickness
        self.pyramidheight = pyramidheight

    def getgraph(self):
        self.xpoints = np.arange(0, 10, 0.1)
        self.ypoints = self.pyramidheight*np.sin(self.xpoints*self.arcthickness)
        plt.clf()
        plt.plot(self.xpoints, self.ypoints)
        fig = plt.gcf()
        # convert graph into dtring buffer and then we convert 64 bit code into image
        # adapted from https://sukhbinder.wordpress.com/2022/04/13/rendering-matplotlib-graphs-in-django/
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        return uri

    def getcsv(self,writer):
        # Iterate through xpoints and ypoints and add to csv file
        writer.writerow(["xpoints", "ypoints"])
        for indx in range(self.xpoints.shape[0]):
            writer.writerow([self.xpoints[indx], self.ypoints[indx]])
        return writer

