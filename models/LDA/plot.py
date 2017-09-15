import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import spline

topic_li = [item for item in range(1,11)]
perplex_li = [202.30983103, 190.514314973, 186.200705153, 179.205489731, 178.612928418, 172.298002847,
170.444798914, 171.820756392, 168.067958487, 163.99150477]

topic_li = np.array(topic_li)
perplex_li = np.array(perplex_li)

topic_smooth = np.linspace(topic_li.min(), topic_li.max(), 400)
per_smooth = spline(topic_li, perplex_li, topic_smooth)


plt.plot(topic_smooth, per_smooth)
plt.xlabel('number of topics', fontsize=16)
plt.ylabel('log(perplexity)', fontsize=16)
plt.show()