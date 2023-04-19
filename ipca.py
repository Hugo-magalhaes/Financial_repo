from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from bcb import sgs
from matplotlib.dates import date2num

hoje = datetime.now()
six_years = hoje - timedelta(365*6)

ipca = sgs.get({'ipca': 433}, start=six_years, end=hoje)
data_numerica = date2num(ipca.index)
fig, ax = plt.subplots()
ax.set_title('IPCA')
ax.plot(data_numerica-7, ipca['ipca'], label='ipca')
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.xaxis_date()
formato_Data = mdates.DateFormatter('%b-%y')
ax.xaxis.set_major_formatter(formato_Data)
plt.legend()
ax.grid(False)
plt.axhline(y=0, color='w')
# plt.savefig('inflacao.png', dpi=300)
plt.show()
