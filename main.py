import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix, plot_confusion_matrix
from sklearn.neural_network import MLPClassifier
from sklearn import tree
from sklearn import preprocessing
import seaborn as sns

regions = ['Latin America & Caribbean', 'South Asia', 'Sub-Saharan Africa', 'Europe & Central Asia', 'Middle East & North Africa', 'East Asia & Pacific', 'North America']
filenameGDP = r'GDP_Per_Capita.xls'
filenameDR = r'DeathRate.xls'
filenameGDP1 = r'GDP.xls'


def scrape(): #scrapes excel sheets and places into dataframes
    dfGDP = pd.read_excel(filenameGDP)
    dfGDP = dfGDP.fillna(-1)
    dfGDP.columns = dfGDP.columns.map(str)

    dfDR = pd.read_excel(filenameDR)
    dfDR = dfDR.fillna(-1)
    
    dfGDP1 = pd.read_excel(filenameGDP1)# for GDP not per Capita
    dfDR1 = pd.read_excel(filenameDR)# for DR with NaN
    return dfGDP, dfDR, dfGDP1, dfDR1


def getDates(dfGDP): #return list of dates for graphing purposes (1960-2020)
    time = []
    for (columnName, columnData) in dfGDP.iteritems():
        if columnName.isnumeric():
            time.append(columnName)
    return time


def getData(index, df): #return data of country at index in dataframe df
    data = []
    for (columnName, columnData) in df.iteritems():
        if (columnName.isnumeric()):
            data.append(columnData[index])
    return data


def getName(index, df): #return name of country at index in dataframe df
    for (columnName, columnData) in df.iteritems():
        if (columnName == 'Country Name'):
            name = columnData[index]
    return name


#seven regions
def getRegionGroups(region): #returns indexes of all tuples of given region - used with mappedlist (regionMap)
    df, dfDR = scrape()
    indexes = []
    for (columnName, columnData) in df.iteritems():
        if (columnName == 'Region'):
            for i in range(0, len(columnData)):
                if region == columnData[i]:
                    indexes.append(i)
    return indexes


def timeSeriesGDP(index, dfGDP): #get timeSeries for specific GDP graph
    time = getDates(dfGDP)
    dataGDP = getData(index, dfGDP)
    name = getName(index, dfGDP)
    plt.plot(time, dataGDP, label=name)
    title = name + ' GDP over Time'
    plt.title(title)
    plt.ylabel('GDP (current US Dollars)')
    plot_finalize()


def timeSeriesGDPregions(dfGDP): #get timeSeries for regions GDP graph
    time = getDates(dfGDP)
    regionMap = map(getRegionGroups, regions)
    for j in range(0, 7):
        currentIndexes = next(regionMap)
        for i in range(0, len(currentIndexes)):
            data = getData(currentIndexes[i], dfGDP)
            plt.plot(time, data, label=getName(currentIndexes[i], dfGDP))
        title = regions[j] + ' GDP over Time'
        plt.title(title)
        plt.ylabel('GDP (current US Dollars)')
        plot_finalize()
        

def timeSeriesDR(index, dfDR): #get timeSeries for specific DR graph
    time = getDates(dfDR)
    dataDR = getData(index, dfDR)
    name = getName(index, dfDR)
    plt.plot(time, dataDR, label=name)
    title = name + ' Death Rate over Time'
    plt.title(title)
    plt.ylabel('Crude Death Rate (per 1000 people)')
    plot_finalize()


def timeSeriesDRregions(dfDR): #get timeSeries for regions DR graph
    time = getDates(dfDR)
    regionMap = map(getRegionGroups, regions)
    for j in range(0, 7):
        currentIndexes = next(regionMap)
        for i in range(0, len(currentIndexes)):
            data = getData(currentIndexes[i], dfDR)
            plt.plot(time, data, label=getName(currentIndexes[i], dfDR))
        title = regions[j] + ' Death Rate over Time'
        plt.title(title)
        plt.ylabel('Crude Death Rate (per 1000 people)')
        plot_finalize()


def plot_finalize(): #finalize plot and show plot
    plt.margins(x=0)
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", prop={'size': 6})
    ax = plt.gca()
    ax.set_xticks(['1960', '1965', '1970', '1975', '1980', '1985', '1990', '1995', '2000', '2005', '2010', '2015', '2020'])
    plt.grid()
    plt.xlabel('Time')
    # plt.show()


def get_country_dictionary(gdp):
    countries = gdp.loc[:, 'Country Name']
    countriesDict = countries.to_dict()
    return countriesDict


def get_total(gdp, dr):
    GDP = gdp.loc[0, ~gdp.columns.isin(['Country Name', 'Country Code', 'Indicator Code', 'Region', 'IncomeGroup', 'Indicator Name'])]
    DR = dr.loc[0, ~dr.columns.isin(['Country Name', 'Country Code', 'Indicator Code', 'Region', 'IncomeGroup', 'Indicator Name'])]

    total_gdp_vals, total_dr_vals, total_country_index_vals = get_total_helper(GDP, DR, 0)
    # start i at 1
    for i in range(1, len(gdp)):
        index = i
        # trim columns to only get years/values
        GDP = gdp.loc[i, ~gdp.columns.isin(['Country Name', 'Country Code', 'Indicator Code', 'Region', 'IncomeGroup', 'Indicator Name'])]
        DR = dr.loc[i, ~dr.columns.isin(['Country Name', 'Country Code', 'Indicator Code', 'Region', 'IncomeGroup', 'Indicator Name'])]
        country_gdp, country_dr, country_index = get_total_helper(GDP, DR, index)

        # add return arrays to the end of our total storage arrays
        total_gdp_vals = np.concatenate((total_gdp_vals, country_gdp))
        total_dr_vals = np.concatenate((total_dr_vals, country_dr))
        total_country_index_vals = np.concatenate((total_country_index_vals, country_index))

    return total_gdp_vals, total_dr_vals, total_country_index_vals


def get_total_helper(gdp, dr, index):
    # merge gdp & dr about year
    data = pd.merge(gdp, dr, right_index=True, left_index=True)
    data.insert(2, 'index', index)
    data.columns = ['_gdp', '_dr', '_index']
    # trim rows where gdp = -1
    # data = data[data['_gdp'] != -1.0]
    data = data.fillna(-1)
    data = data.to_numpy()
    # split
    dataGDP, dataDR, country_index = np.hsplit(data, 3)

    return dataGDP, dataDR, country_index


def plot_regression(x_test, y_test, y_pred, title):
    plt.scatter(x_test, y_test)
    plt.plot(x_test, y_pred, color="black", linewidth=3)
    # add amount to y label(mil, bil, tril)
    plt.xlabel('Death Rate crude per 1000 people')
    plt.ylabel('GDP')
    plt.title(title)
    plt.show()
    plt.clf()


# line has terrible fit, perhaps separate gdp values based on gdp > x and gdp < x
def regression(gdp, dr, index):
    plt.clf()
    modified_data = np.concatenate((gdp, dr, index), axis=1)
    # remove -1 vals from both sets
    modified_data = np.delete(modified_data, np.where(modified_data[:, 0] == -1.0), axis=0)
    modified_data = np.delete(modified_data, np.where(modified_data[:, 1] == -1.0), axis=0)
    # removes outliers
    # modified_data = np.delete(modified_data, np.where(modified_data[:, 0] > 1775), axis=0)
    modified_data = np.delete(modified_data, np.where(modified_data[:, 1] > 20.171), axis=0)
    mod_gdp, mod_dr, mod_ind = np.hsplit(modified_data, 3)
    # apply log scale on gdp
    mod_gdp = np.log10(mod_gdp)
    # checks for outliers
    # sns.boxplot(mod_gdp)
    # plt.show()

    # regression on all data points
    x_train, x_test, y_train, y_test = train_test_split(mod_dr, mod_gdp, test_size=0.2)
    regr = linear_model.LinearRegression()
    regr.fit(x_train, y_train)
    y_pred = regr.predict(x_test)

    # print(regr.coef_)
    # print(mean_squared_error(y_test, y_pred))

    # 1 is perfect fit
    # print(r2_score(y_test, y_pred))

    plot_regression(x_test, y_test, y_pred, 'Regression: All Countries')

    # REGRESSION ON UNITED STATES ##########################################
    modified_data = np.concatenate((gdp, dr, index), axis=1)
    # excel ind - 2 = country u want (remove -1 from both sets if other country)
    modified_data = np.delete(modified_data, np.where(modified_data[:, 2] != 253-2), axis=0)
    mod_gdp, mod_dr, mod_ind = np.hsplit(modified_data, 3)
    # decide whether to keep or discard log scale for single country
    mod_gdp = np.log10(mod_gdp)

    x_train, x_test, y_train, y_test = train_test_split(mod_dr, mod_gdp, test_size=0.50)
    regr = linear_model.LinearRegression()
    regr.fit(x_train, y_train)
    y_pred = regr.predict(x_test)

    # 1 is perfect fit
    # print(r2_score(y_test, y_pred))

    # plot_regression(x_test, y_test, y_pred, 'Regression: U.S.')


def single_year_regression(gdp, dr):
    # get 2020 data
    GDP = gdp.loc[:, gdp.columns.isin(['2020'])]
    DR = dr.loc[:, dr.columns.isin(['2020'])]

    data = pd.merge(GDP, DR, right_index=True, left_index=True).dropna().to_numpy()
    data = np.delete(data, np.where(data[:, 0] == -1.0), axis=0)
    data = np.delete(data, np.where(data[:, 0] > 2E10), axis=0)

    GDP, DR = np.hsplit(data, 2)
    GDP = np.log10(GDP)

    # regression
    x_train, x_test, y_train, y_test = train_test_split(DR, GDP)
    regr = linear_model.LinearRegression()
    regr.fit(x_train, y_train)
    y_pred = regr.predict(x_test)

    # 1 is perfect fit
    # print(r2_score(y_test, y_pred))

    # plot_regression(x_test, y_test, y_pred, 'Regression: All Countries Year 2020')
    
    def cleanData (dfGDP, dfDR):#get rid of the features besides IncomeGroup and GDP and Death rate 
    GDP = dfGDP.drop(labels=['Country Code', 'Region', 'Indicator Name','Indicator Code', "Country Name"], axis=1)
    GDP = GDP.dropna(subset = ["IncomeGroup"])
    GDP = GDP.replace(-1, 0)
    
    DR = dfDR.drop(labels=['Country Code', 'Region', 'Indicator Name','Indicator Code', "Country Name"], axis=1)
    DR = DR.dropna(subset = ["IncomeGroup"])
    DR = DR.fillna(0)
    
    return GDP, DR 

def getXy(GDP, DR):
    #normalizing the data and generated the X and y
    y = GDP.loc[:, 'IncomeGroup'].to_numpy()
    X1 = GDP.iloc[:, 1:62]
    X1d = preprocessing.normalize(X1, axis=0)
    X2 = DR.iloc[:, 1:62]
    X2d = preprocessing.normalize(X2, axis=0)
    X = np.concatenate((X1d, X2d), axis = 1)
    return X,y

def getAvg(GDP, DR): # use the avg as training and testing data
    avgGDP = GDP.mean(axis=1)
    avgDR = DR.mean(axis=1)
    Xavg = np.vstack((avgGDP,avgDR))
    return Xavg

def MLPandcm (X_train, X_test, y_train, y_test):
    clf = MLPClassifier(activation='tanh', hidden_layer_sizes=(200,150), max_iter=1500)
    clf.fit(X_train, y_train)
    test_pred = clf.predict(X_test)
    train_pred = clf.predict(X_train)
    print("MLP Classifier")
    print("The testing accuracy score is: " + str(accuracy_score(y_test, test_pred)))
    print("The testing accuracy score for X_train is: " + str(accuracy_score(y_train, train_pred)))
    plot_confusion_matrix(clf, X_test, y_test)  
    plt.xticks(rotation = 45)
    plt.show()

def DTandcm (X_train, X_test, y_train, y_test):
    clf = tree.DecisionTreeClassifier().fit(X_train, y_train)
    test_pred = clf.predict(X_test)
    train_pred = clf.predict(X_train)
    print("Decision Tree Classifier")
    print("The testing accuracy score is: " + str(accuracy_score(y_test, clf.predict(X_test))))
    print("The testing accuracy score for X_train is: " + str(accuracy_score(y_train, clf.predict(X_train))))
    plot_confusion_matrix(clf, X_test, y_test)
    plt.xticks(rotation = 45)
    plt.show()


if __name__ == '__main__':
    df_GDP, df_DR = scrape()
    timeSeriesDR(54, df_DR)
    timeSeriesGDP(76, df_GDP)
    timeSeriesGDPregions(df_GDP)
    timeSeriesDRregions(df_DR)

    total_gdp, total_dr, total_country_index = get_total(df_GDP, df_DR)

    regression(total_gdp, total_dr, total_country_index)
    single_year_regression(df_GDP, df_DR)
    
    GDP, DR = cleanData(df_GDP1, df_DR1)
    X, y = getXy(GDP, DR)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    MLPandcm (X_train, X_test, y_train, y_test)
    DTandcm (X_train, X_test, y_train, y_test)
    
    Xavg = getAvg(GDP, DR)
    X_avg_train, X_avg_test, y_avg_train, y_avg_test = train_test_split(Xavg.transpose(), y, test_size=0.2)
    MLPandcm (X_avg_train, X_avg_test, y_avg_train, y_avg_test)
    DTandcm (X_avg_train, X_avg_test, y_avg_train, y_avg_test)
    