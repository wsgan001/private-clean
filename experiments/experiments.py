
from generate_dataset import generate
from query import distinct_count, countq, sumq, avgq
import numpy
import math

def run_T_trials(trials=100,
				 size=1000,
				 cprivacy=0.1,
				 nprivacy=1,
				 distinct=10,
				 selectivity=0.5,
				 errorrate=0.21,
				 cskew=0.33,
				 nskew=0.33):

	sumr = []
	countr = []
	avgr = []

	for t in range(0,trials):
		#print "Running Trial ", t
		dataset = generate(S=size,p=cprivacy,b=nprivacy,N=distinct,z1=cskew,z2=nskew)
		truepred = range(int(round((1-selectivity)*distinct)),distinct)#numpy.random.choice(range(0,distinct),size=int(round(selectivity*distinct)),replace=False)
		corruptpred = []

		if int(round(errorrate*distinct)) >= 1: 
			corruptpred = numpy.random.choice(range(0,distinct),size=int(round(errorrate*distinct)),replace=False)

		corruptpred = list(set(truepred).union(set(corruptpred)))

		sum_cresult = sumq(dataset, predicate=truepred,p=cprivacy,b=nprivacy)
		count_cresult = countq(dataset, predicate=truepred,p=cprivacy)
		avg_cresult = avgq(dataset, predicate=truepred,p=cprivacy,b=nprivacy)

		sum_dresult = sumq(dataset, predicate=corruptpred,p=cprivacy,b=nprivacy)
		count_dresult = countq(dataset, predicate=corruptpred,p=cprivacy)
		avg_dresult = avgq(dataset, predicate=corruptpred,p=cprivacy,b=nprivacy)

		if count_cresult[2] > 0:
			sumr.append((sum_cresult[0],sum_dresult[1],sum_cresult[2],sum_dresult[2]))
			countr.append((count_cresult[0],count_dresult[1],count_cresult[2],count_dresult[2]))
			avgr.append((avg_cresult[0],avg_dresult[1],avg_cresult[2],avg_dresult[2]))

	return (sumr,countr,avgr)

def l1_error(result_tuple, query='sum'):
	index = 0
	if query == 'sum':
		index = 0
	elif query == 'count':
		index = 1
	else:
		index = 2
	
	errors = [ [100*numpy.abs(r[0]-r[2])/max(r[2],1),100*numpy.abs(r[1]-r[2])/max(r[2],1),100*numpy.abs(r[3]-r[2])/max(r[2],1)] for r in result_tuple[index]]
	
	return (numpy.mean(errors,axis=0), numpy.std(errors,axis=0))

def plot_parameter_sweep(exp_lambda,
						 parameters,
						 xaxis="",
						 yaxis="",
						 title="",
						 filename="output.png"):
	
	import matplotlib.pyplot as plt
	from matplotlib import font_manager, rcParams

	plt.figure()

	X = parameters
	Y1 = []
	E1 = []

	Y2 = []
	E2 = []

	Y3 = []
	E3 = []

	for x in X:
		result = exp_lambda(x)
		Y1.append(result[0][0])
		E1.append(result[1][0])

		Y2.append(result[0][1])
		E2.append(result[1][1])

		Y3.append(result[0][2])
		E3.append(result[1][2])

	rcParams.update({'font.size': 22})

	fprop = font_manager.FontProperties(fname= 
        '/Library/Fonts/Microsoft/Gill Sans MT.ttf') 

	plt.plot(X, Y1, 's-', linewidth=2.5,markersize=16,color='#3399FF')
	plt.plot(X, Y2, 'o-', linewidth=2.5,markersize=16,color='#FF6666')
	plt.plot(X, Y3, '--')
	plt.title(title,fontproperties=fprop)
	plt.xlabel(xaxis,fontproperties=fprop)
	plt.ylabel(yaxis,fontproperties=fprop)
	xticklabels = plt.getp(plt.gca(), 'xticklabels') 
	xticklabels = plt.getp(plt.gca(), 'yticklabels') 
	plt.setp(xticklabels, fontproperties=fprop) 
	#plt.legend(['PrivateClean','Naive', 'Dirty'], loc='upper left')
	plt.grid(True)
	plt.savefig(filename)
