# import pandas as pd
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages


vehicle_growthRate = 0.01 # 1% growth p.a.
annualNewCars = 1000000 # count # current number of new cars in Australia bought annually
ICEV_embodiedEnergy = 16.3 # tCO2 -- sourced from https://www.volvocars.com/images/v/-/media/market-assets/intl/applications/dotcom/pdf/c40/volvo-c40-recharge-lca-report.pdf
EV_embodiedEnergy = 26.9 # tCO2 -- sourced from https://www.volvocars.com/images/v/-/media/market-assets/intl/applications/dotcom/pdf/c40/volvo-c40-recharge-lca-report.pdf
distTravPA = 12000 # km/year # average distance travelled by an Australian car
sharedVehicleDistTravPA = 50000 # this was used to explore some other scenarios, currently unused
ICEV_fuelEconomy = 0.25 # kgCO2/km # average CO2 emissions for a petrol/diesel car in Australia
EV_fuelEconomy = 0.01 # kgCO2/km # average CO2 emissions for an electric car in Australia is 0.02 kgCO2/km

# CO2 limits
# sector data from https://www.csiro.au/en/research/environmental-impacts/climate-change/Climate-change-QA/Sources-of-GHG-gases
# CO2 budget from https://theconversation.com/renewable-energy-breeding-can-stop-australia-blowing-the-carbon-budget-if-were-quick-94032
# calculate the CO2 budgets by the total Australian budget for each limit, multiplied by the proportion of Australia's emissions that
# come from the transport sector
lim2C = .176 * 3300 # Mt
lim15C = .176 * 1300 # Mt

years = range(2022,2065,1)
years = [int(i) for i in years]

def plotScenario(scn, name, desc, shared):
    import matplotlib.pyplot as plt
    with PdfPages(name + "time_series.pdf") as export_pdf:
        plt.figure(figsize=(11, 9))
        plt.subplot(411)
        plt.stackplot(scn['year'], scn['numEVs'], scn['numICEVs'])
        plt.legend(['EVs', 'ICEVs'])
        plt.title('desc')
        plt.ylabel('numbers of ICEVs and EVs')
        # plt.figure()

        # plt.plot(years, scn['totalNumCars'], 'tab:blue')
        # plt.title(desc)
        plt.subplot(413)
        plt.plot(scn['cumulativeEmissions'])
        plt.ylabel('cumulative emissions (Mt)')
        # plt.plot(years, scn['numEVs'], 'tab:blue')
        plt.subplot(412)
        plt.stackplot(scn['year'], scn['embodiedEmissions'], scn['usageEmissions'])
        plt.ylabel('annual emissions breakdown (Mt)')
        plt.legend(['embodied', 'point-of-use'])

        plt.subplot(414)
        if shared:
            plt.plot(years, [i/1000000 for i in scn['annualDistTrav']], 'tab:blue')
        else:
            plt.plot(years, [i * distTravPA / 1000000 for i in scn['totalNumCars']], 'tab:blue')
        plt.ylabel('total annual light vehicle distance travelled (millions km)')
        # plt.subplot(412)
        export_pdf.savefig()

        plt.title(desc)
        plt.close()
    # plt.plot(years, scn['numEVs'], 'tab:blue')
    # plt.show()

def calcEmissions(scn):
    scn['embodiedEmissions'] = list()
    scn['usageEmissions'] = list()
    scn['totalEmissions'] = list()
    scn['annualDistTrav'] = list() #[distTravPA*scn['numICEVs'][0]]
    for idx, year in enumerate(scn['year']):
        scn['embodiedEmissions'].append((scn['newEVs'][idx] * EV_embodiedEnergy +
                                        scn['newICEVs'][idx] * ICEV_embodiedEnergy) / 1000000) # Mt
        if 'distTravelPA' in scn.keys():
            scn['usageEmissions'].append((scn['numEVs'][idx] * scn['distTravelPA'][idx] * EV_fuelEconomy +
                                     scn['numICEVs'][idx] * scn['distTravelPA'][idx] * ICEV_fuelEconomy) / 1000000000) # Mt
        else:
            scn['usageEmissions'].append((scn['numEVs'][idx] * distTravPA * EV_fuelEconomy +
                                          scn['numICEVs'][idx] * distTravPA * ICEV_fuelEconomy) / 1000000000)  # Mt
        scn['totalEmissions'].append(scn['embodiedEmissions'][idx] + scn['usageEmissions'][idx])
        scn['annualDistTrav'].append(scn['numEVs'][idx]*sharedVehicleDistTravPA + scn['numICEVs'][idx]*distTravPA)
    scn['cumulativeEmissions'] = np.cumsum(scn['totalEmissions']) # Mt
    return scn

# Scenario 1:
# 1E6 new ICEVs each year
# total number of cars grows at 1% p.a.
scn = dict()
scn['year'] = years
scn['numEVs'] = list()
scn['numEVs'].append(0)
scn['newEVs'] = list()
scn['newEVs'].append(0)
scn['totalNumCars'] = list()
scn['totalNumCars'].append(20000000)
scn['numICEVs'] = list()
scn['numICEVs'].append(20000000)
scn['newICEVs'] = list()
scn['newICEVs'].append(1000000) #20000000*vehicle_growthRate)
for idx, year in enumerate(years):
    if idx == 0: continue
    scn['newICEVs'].append(1000000) #round(scn['totalNumCars'][idx-1]*vehicle_growthRate))
    scn['newEVs'].append(0)
    scn['totalNumCars'].append(scn['totalNumCars'][idx-1] * (1 + vehicle_growthRate)) # + scn['newICEVs'][idx-1])
    scn['numEVs'].append(scn['numEVs'][idx-1] + scn['newEVs'][idx-1]) # no new EVs
    scn['numICEVs'].append(scn['totalNumCars'][idx] - scn['numEVs'][idx])

    # test scenario
    assert(scn['numEVs'][idx] + scn['numICEVs'][idx] == scn['totalNumCars'][idx])
    if idx > 0:
        assert(round(scn['numEVs'][idx-1] + scn['newEVs'][idx-1]) == scn['numEVs'][idx])

# checkScenario(scn)
scn1 = calcEmissions(scn)

# Scenario 2: All new cars are EVs, EVs not shared
scn = dict()
scn['year'] = years
scn['numEVs'] = list()
scn['numEVs'].append(0)
scn['newEVs'] = list()
scn['newEVs'].append(1000000)
scn['totalNumCars'] = list()
scn['totalNumCars'].append(20000000)
scn['numICEVs'] = list()
scn['numICEVs'].append(20000000)
scn['newICEVs'] = list()
scn['newICEVs'].append(0)
for idx, year in enumerate(years):
    if idx == 0: continue
    scn['newICEVs'].append(0)
    scn['newEVs'].append(1000000)
    scn['totalNumCars'].append(round(scn['totalNumCars'][idx-1] * (1 + vehicle_growthRate)))
    scn['numEVs'].append(min(scn['numEVs'][idx-1] + scn['newEVs'][idx-1],scn['totalNumCars'][idx])) # no new EVs
    scn['numICEVs'].append(scn['totalNumCars'][idx] - scn['numEVs'][idx])

    #test scenario
    assert (scn['numEVs'][idx] + scn['numICEVs'][idx] == scn['totalNumCars'][idx])
# checkScenario(scn)
scn2 = calcEmissions(scn)

# # Scenario 3:
# # All new cars are EVs, and each EV replaces 2 ICEVs (due to sharing of EVs)
# # Also, total car use decreases because of increased use of public transport and active transport
# scn = dict()
# scn['year'] = years
# scn['numEVs'] = list()
# scn['numEVs'].append(0)
# scn['newEVs'] = list()
# scn['newEVs'].append(1000000)
# scn['totalNumCars'] = list()
# scn['totalNumCars'].append(20000000)
# scn['numICEVs'] = list()
# scn['numICEVs'].append(20000000)
# scn['newICEVs'] = list()
# scn['newICEVs'].append(0)
# # scn['perCarDistTravelled'] = range()
# newEVrate = 500000
# for idx, year in enumerate(years):
#     if idx == 0: continue
#     scn['newICEVs'].append(0)
#     scn['newEVs'].append(newEVrate)
#     scn['numEVs'].append(scn['numEVs'][idx-1] + scn['newEVs'][idx-1])
#     scn['totalNumCars'].append(round(scn['totalNumCars'][idx-1] * (1 + vehicle_growthRate)))
#     scn['numICEVs'].append(max(scn['totalNumCars'][idx] - scn['numEVs'][idx]*2,0))
#     if scn['numICEVs'][idx] == 0:
#         newEVrate = 0
#         vehicle_growthRate = 0
#     # test scenario
#     try:
#         assert (scn['numEVs'][idx] * 2 + scn['numICEVs'][idx] == scn['totalNumCars'][idx])
#     except:
#         assert (scn['numEVs'][idx] * 2 > scn['totalNumCars'][idx])
# # checkScenario(scn)
# scn3 = calcEmissions(scn)
#
# # Scenario 4:
# # All new cars are EVs,
# # Also, total car use decreases by increased use of public transport and active transport
# scn = dict()
# scn['year'] = years
# scn['numEVs'] = list()
# scn['numEVs'].append(0)
# scn['newEVs'] = list()
# scn['newEVs'].append(1000000)
# scn['totalNumCars'] = list()
# scn['totalNumCars'].append(20000000)
# scn['numICEVs'] = list()
# scn['numICEVs'].append(20000000)
# scn['newICEVs'] = list()
# scn['newICEVs'].append(0)
# scn_vehicleGrowthRate = 0.95
# # scn['perCarDistTravelled'] = range()
# newEVrate = 500000
# for idx, year in enumerate(years):
#     if idx == 0:
#         continue
#     scn['newICEVs'].append(0)
#     scn['totalNumCars'].append(round(scn['totalNumCars'][idx-1] * scn_vehicleGrowthRate))
#     scn['newEVs'].append(newEVrate)
#     scn['numEVs'].append(scn['numEVs'][idx-1] + scn['newEVs'][idx-1])
#     scn['numICEVs'].append(max(scn['totalNumCars'][idx] - scn['numEVs'][idx],0))
#     if scn['numICEVs'][idx] == 0:
#         newEVrate = 0
#     # test scenario
#     try:
#         assert (scn['numEVs'][idx] + scn['numICEVs'][idx] == scn['totalNumCars'][idx])
#     except:
#         assert(scn['numEVs'][idx] > scn['totalNumCars'][idx])
# # checkScenario(scn)
# scn4 = calcEmissions(scn)

# Scenario 5:
# no new cars at all
# total number of cars and total distance travelled reduces 8% annually
scn = dict()
scn['year'] = years
scn['numEVs'] = list()
scn['numEVs'].append(0)
scn['newEVs'] = list()
scn['newEVs'].append(0)
scn['totalNumCars'] = list()
scn['totalNumCars'].append(20000000)
scn['numICEVs'] = list()
scn['numICEVs'].append(20000000)
scn['newICEVs'] = list()
scn['newICEVs'].append(0)
scn_vehicleGrowthRate = 0.92
# scn['perCarDistTravelled'] = range()
for idx, year in enumerate(years):
    if idx == 0:
        continue
    scn['newICEVs'].append(0)
    scn['totalNumCars'].append(round(scn['totalNumCars'][idx-1] * scn_vehicleGrowthRate))
    scn['newEVs'].append(0)
    scn['numEVs'].append(scn['numEVs'][idx-1] + scn['newEVs'][idx-1])
    scn['numICEVs'].append(max(scn['totalNumCars'][idx] - scn['numEVs'][idx]*2,0))

    # test scenario
    assert (scn['numEVs'][idx] + scn['numICEVs'][idx] == scn['totalNumCars'][idx])
    
# checkScenario(scn)
scn5 = calcEmissions(scn)


# plotScenario(scn)
print('')
import matplotlib.pyplot as plt

descs = ['1 million new ICEVs p.a., no new EVs','1 million new EVs p.a., no new ICEVs', '1 million new EVs p.a., no new ICEVs, each new EV replaces two ICEVs', '1 million new EVs p.a., no new ICEVs, each new EV replaces two ICEVs and number of cars reduces at \n8% p.a. until all cars are EVs', 'no new cars at all, reduce total distance travelled by 8% p.a.']
with PdfPages("cumulative_emissions.pdf") as export_pdf:
    plt.figure(figsize=(11, 9))
    plt.subplot(211)
    plt.plot(years, scn1['cumulativeEmissions'], 'tab:brown')
    plt.plot(years, scn2['cumulativeEmissions'], 'tab:blue')
    # plt.plot(years, scn3['cumulativeEmissions'], 'tab:purple')
    # plt.plot(years, scn4['cumulativeEmissions'], 'tab:green')
    plt.plot(years, scn5['cumulativeEmissions'], 'tab:cyan')
    plt.plot(years, [lim2C] * len(years), 'tab:red', alpha=0.4)
    plt.plot(years, [lim15C] * len(years), 'tab:orange', alpha=0.4)
    plt.text(years[10], lim2C+ 10, '2C CO2 emissions limit for transport', color='tab:red', alpha=0.4)
    plt.text(years[10], lim15C+ 10, '1.5C CO2 emissions limit for transport',color='tab:orange', alpha=0.4)
    plt.ylabel('cumulative CO2 emissions from Australian transport (Mt)')
    plt.xlabel('year')
    plt.legend([descs[0], descs[1], descs[-1]])
    plt.title('cumulative emissions from light motorised transport in Australia under 4 different scenarios')
    # plt.subplot(212)
    # plt.plot(years, [i * distTravPA / 1000000 for i in scn1['totalNumCars']], 'tab:brown')
    # plt.plot(years, [i * distTravPA / 1000000 for i in scn2['totalNumCars']], 'tab:blue')
    # plt.plot(years, [i/1000000 for i in scn3['annualDistTrav']], 'tab:purple')
    # plt.plot(years, [i/1000000 for i in scn4['annualDistTrav']], 'tab:green')
    # plt.plot(years, [i * distTravPA / 1000000 for i in scn5['totalNumCars']], 'tab:cyan')
    # plt.legend(descs)
    plt.title('annual total distance travelled by light motorised transport\nin Australia under 4 different scenarios (million kn)')
    export_pdf.savefig()

# with PdfPages("light_vehicle_total_distance_travelled.pdf") as export_pdf:
#     plt.figure(figsize=(11, 9))
#     plt.plot(years, [i * distTravPA/1000000 for i in scn1['totalNumCars']], 'tab:brown')
#     plt.plot(years, [i * distTravPA/1000000 for i in scn2['totalNumCars']], 'tab:blue')
#     plt.plot(years, [i/1000000 for i in scn3['annualDistTrav']], 'tab:purple')
#     plt.plot(years, [i/1000000 for i in scn4['annualDistTrav']], 'tab:green')
#     plt.plot(years, [i * distTravPA/1000000 for i in scn5['totalNumCars']], 'tab:cyan')
#     plt.legend(descs)
#     plt.title('annual total distance travelled by light motorised transport\nin Australia under 4 different scenarios (million km)')
#     export_pdf.savefig()
#
plotScenario(scn1, 'scn1', descs[0], shared=False)
plotScenario(scn2, 'scn2', descs[1], shared=False)
# # plotScenario(scn3, 'scn3', descs[2], shared=True)
# # plotScenario(scn4, 'scn4', descs[3], shared=True)
plotScenario(scn5, 'scn5', descs[4], shared=False)
