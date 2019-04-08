# -*- coding: utf-8 -*-
import math
import codecs
import random

class KMeans:

    def getColMedian(self,colList):
        tmp = list(colList)
        tmp.sort()
        alen = len(tmp)
        if alen % 2 == 1:
            return tmp[alen // 2]
        else:
            return (tmp[alen // 2] + tmp[(alen // 2) - 1]) / 2

    def colNormalize(self,colList):
        median = self.getColMedian(colList)
        asd = sum([abs(x - median) for x in colList]) / len(colList)
        result = [(x - median) / asd for x in colList]
        return result

    '''
    1.read data by column
    2.normalize the data
    3.select k cluster center randomly
    4.allocate the data according to distance to the cluster center
    '''
    def __init__(self,filePath,k):
        self.data={}
        self.k=k
        self.iterationNumber=0
        self.pointsChanged=0
        self.SSE=0
        line_1=True
        with codecs.open(filePath,'r','utf-8') as f:
            for line in f:
                if line_1:
                    line_1=False
                    header=line.split(',')
                    self.cols=len(header)
                    # print "cols: " + len(cols)
                    self.data=[[] for i in range(self.cols)]
                else:
                    instances=line.split(',')
                    column_0=True
                    for ins in range(self.cols):
                        if column_0:
                            self.data[ins].append(instances[ins])
                            column_0=False
                        else:
                            self.data[ins].append(float(instances[ins]))
        self.dataSize=len(self.data[1])
        self.memberOf=[-1 for x in range(self.dataSize)]

        for i in range(1,self.cols):
            self.data[i]=self.colNormalize(self.data[i])

        random.seed()
        # if you only need the normal k-means selecting, use the code below:
        # self.centroids=[[self.data[i][r] for i in range(1,self.cols)]
        #                for r in random.sample(range(self.dataSize),self.k)]

        # or use the k-mean++ center selecting below
        self.selectInitialCenter()

        self.assignPointsToCluster()

    def assignPointToCluster(self,i):
        min=10000
        clusterNum=-1
        for centroid in range(self.k):
            dist=self.distance(i,centroid)
            if dist<min:
                min=dist
                clusterNum=centroid
        # track the points that changes their belonging center
        if clusterNum!=self.memberOf[i]:
            self.pointsChanged+=1
        self.SSE+=min**2
        return clusterNum

    def assignPointsToCluster(self):
        self.pointsChanged=0
        self.SSE=0
        self.memberOf=[self.assignPointToCluster(i) for i in range(self.dataSize)]

    def distance(self,i,j):
        sumSquares=0
        for k in range(1,self.cols):
            sumSquares+=(self.data[k][i]-self.centroids[j][k-1])**2
        return math.sqrt(sumSquares)

    def updateCenter(self):
        members=[self.memberOf.count(i) for i in range(len(self.centroids))]
        self.centroids=[
            [sum([self.data[k][i] for i in range(self.dataSize)
                  if self.memberOf[i]==centroid])/members[centroid]
             for k in range(1,self.cols)]
            for centroid in range(len(self.centroids))]

    '''
    update the cluster center and re-allocate them
    until the percent of chaning members in cluster less then 1%
    '''
    def cluster(self):
        done=False
        while not done:
            self.iterationNumber+=1
            self.updateCenter()
            self.assignPointsToCluster()
            if float(self.pointsChanged)/len(self.memberOf)<0.01:
                done=True
        print("(SSE): %f" % self.SSE)

    def printResults(self):
        for centroid in range(len(self.centroids)):
            print('\n\nCategory %i\n=========' % centroid)
            for name in [self.data[0][i] for i in range(self.dataSize)
                if self.memberOf[i]==centroid]:
                print(name)

    # kmeans++ cluster center init
    def selectInitialCenter(self):
        centroids=[]
        total=0
        firstCenter=random.choice(range(self.dataSize))
        centroids.append(firstCenter)
        for i in range(0,self.k-1):
            weights=[self.distancePointToClosestCenter(x,centroids)
                     for x in range(self.dataSize)]
            total=sum(weights)
            weights=[x/total for x in weights]

            num=random.random()
            total=0
            x=-1
            while total<num:
                x+=1
                total+=weights[x]
            centroids.append(x)
        self.centroids=[[self.data[i][r] for i in range(1,self.cols)] for r in centroids]

    def distancePointToClosestCenter(self,x,center):
        result=self.eDistance(x,center[0])
        for centroid in center[1:]:
            distance=self.eDistance(x,centroid)
            if distance<result:
                result=distance
        return result

    def eDistance(self,i,j):
        sumSquares=0
        for k in range(1,self.cols):
            sumSquares+=(self.data[k][i]-self.data[k][j])**2
        return  math.sqrt(sumSquares)

'''
usage:
1. input the tuples in clusterSet.txt (reference: clusterSetSample.txt)
2. input the cluster number
3. run this script
4. the result would be printed into console
'''
if __name__=='__main__':
    kmeans=KMeans('clusterSet.txt',3)
    kmeans.cluster()
    kmeans.printResults()