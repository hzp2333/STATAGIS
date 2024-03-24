'''
Reference：
[1] https://blog.csdn.net/sinat_17196995/article/details/69621687
[2] GitHub: https://github.com/stonycat/ML-in-Action-Code-and-Note
'''
import lpsolve_wrapper as lw
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import concurrent.futures
import time
import copy

plt.rc('font',family='Times New Roman')


def lp(minimize , obj, con, dirc, rhs):
    model = lw.Model(
    notations={
        'x': lw.notation(
            shape=obj.shape[0],
            upper_bound=np.inf,
            lower_bound=0,  )    })

    for row in range(con.shape[0]):
        model.add_constr_mat(
        coef_mats={"x":con[row]},
        right_value=rhs[row],
        constr_type=dirc[row]
        )

    objective, notation_list = model.lp_solve(
        obj_func={
            'x': obj,
        },
        minimize=minimize
    )
    return objective,notation_list


def solvelp(i, obj, conFrontier, dirc, gCoef, base):
    baseIdNth = base[i]
    rhs = baseIdNth
    conG = np.multiply(gCoef, rhs)[:, np.newaxis]

    con = np.concatenate((conG, conFrontier), axis=1)

    objective, notation_list = lp(False , obj, con, dirc, rhs)
    sol = notation_list["x"]
    return sol[0].sum()


def ddf(data, goodStart=2, goodNum=1, badNum=1, inputNum=3):
    gbiNum = goodNum + badNum + inputNum
    base = data[:, goodStart:goodStart + gbiNum]
    frontier = data[:, goodStart:goodStart + gbiNum]

    gCoef = np.concatenate((np.tile(-1, goodNum), np.tile(1, badNum), np.tile(0, inputNum)))

    base = np.array(base)
    frontier = np.array(frontier)
    if (base.shape[1]) != (frontier.shape[1]):
        print("Number of columns of the base matrix and the frontier matrix is not identical!")

    baseIdNum = base.shape[0]
    frontierIdNum = frontier.shape[0]

    obj = np.concatenate((np.array([1]), np.zeros(frontierIdNum)), axis=0)
    dirc = np.concatenate((np.tile(lw.GEQ, goodNum), np.tile(lw.EQ, badNum), np.tile(lw.LEQ, inputNum)))[:, np.newaxis]

    conFrontier = frontier.T

    dictt = {}
    with concurrent.futures.ThreadPoolExecutor() as pool:
        results = {pool.submit(solvelp, i, obj, conFrontier, dirc, gCoef, base): i for i in (range(baseIdNum))}
        for f in concurrent.futures.as_completed(results.keys()):

            dictt[results[f]] = f.result()

    df1 = pd.DataFrame(pd.Series(dictt)).T.sort_index(ascending=True)

    data2 = np.concatenate((data[:,0:2],np.array(df1).reshape(-1,1)),axis =1)
    return data2

def binSplitDataSet(dataSet, feature, value):
    mat0 = dataSet[np.nonzero(dataSet[:, feature] > value)[0], :]
    mat1 = dataSet[np.nonzero(dataSet[:, feature] <= value)[0], :]
    return mat0, mat1

def regLeaf(re):
    return np.mean(re).round(3)


def regErr(re):
    return np.var(re) * np.shape(re)[0]

def featIndexparse(featIndex,dataSet,tolN,goodNum,badNum,inputNum,errType,leafType,Mean):


    bestS2 = np.inf
    bestValue2 = 0
    for splitVal in tqdm(set((dataSet[:, featIndex].T.A.tolist())[0])):  # 遍历每个特征里不同的特征值
        mat0, mat1 = binSplitDataSet(dataSet, featIndex, splitVal)  # 对每个特征进行二元分类
        if (np.shape(mat0)[0] < tolN) or (np.shape(mat1)[0] < tolN):
            continue
        reMat0IdYear = ddf(data=mat0, goodStart=2, goodNum=goodNum, badNum=badNum, inputNum=inputNum)
        reMat1IdYear = ddf(data=mat1, goodStart=2, goodNum=goodNum, badNum=badNum, inputNum=inputNum)
        newS = errType(reMat0IdYear[:, 2]) + errType(reMat1IdYear[:, 2])

        newMean0 = leafType(reMat0IdYear[:, 2])
        newMean1 = leafType(reMat1IdYear[:, 2])
        if (newMean0 >= Mean) or (newMean1 >= Mean):
            continue

        if newS < bestS2:

            bestS2 = newS
            bestValue2 = splitVal

    return  bestValue2 , bestS2


def chooseBestSplit(
        dataSet,
        leafType=regLeaf,
        errType=regErr,
        ops=(0, 1),
        ddfp=(2, 1, 1, 3),
        colName=["colName"]):

    tolS = ops[0]
    tolN = ops[1]

    goodStart = ddfp[0]
    goodNum = ddfp[1]
    badNum = ddfp[2]
    inputNum = ddfp[3]
    gbiNum = goodNum + badNum + inputNum

    featureN = goodStart + gbiNum

    reIdYear = ddf(data=dataSet, goodStart=2, goodNum=goodNum, badNum=badNum, inputNum=inputNum)
    reF = reIdYear

    m, n = np.shape(dataSet)
    S = errType(reIdYear[:, 2])
    bestS = np.inf
    bestIndex = 0
    bestValue = 0
    Mean = leafType(reIdYear[:, 2])

    if len(set(dataSet[:, featureN:n].T.tolist()[0])) == 1:
        print("1")
        return reIdYear, None,None, leafType(reIdYear[:, 2])


    featIndexlt = range(featureN, n)


    dictt = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=20) as pool:

        results = [pool.submit(featIndexparse, featIndex,dataSet,tolN,goodNum,badNum,inputNum,errType,leafType,Mean) for featIndex in featIndexlt]
        for featIndex,f in zip(featIndexlt,(results)):
            dictt[featIndex]=f.result()



    for featIndexDict,splitVal_newSDict in dictt.items():

        if splitVal_newSDict[1] < bestS:
            print(featIndexDict,"换了")
            bestIndex = featIndexDict
            bestValue = splitVal_newSDict[0]
            bestS = splitVal_newSDict[1]
        else:
            print(featIndexDict,"没换")
    print("bestIndex:",bestIndex)
    print("bestValue:",bestValue)
    bestmat0, bestmat1 = binSplitDataSet(dataSet, bestIndex, bestValue)
    print(np.shape(bestmat0)[0],np.shape(bestmat1)[0])
    if (np.shape(bestmat0)[0] < tolN) or (np.shape(bestmat1)[0] < tolN):
        print("3")
        return reIdYear, None, None,leafType(reIdYear[:, 2])
    bestreMat0IdYear = ddf(data=bestmat0, goodStart=2, goodNum=goodNum, badNum=badNum, inputNum=inputNum)
    bestreMat1IdYear = ddf(data=bestmat1, goodStart=2, goodNum=goodNum, badNum=badNum, inputNum=inputNum)
    newMean00 = leafType(bestreMat0IdYear[:, 2])
    newMean11 = leafType(bestreMat1IdYear[:, 2])
    if (newMean00 >= Mean) or (newMean11 >= Mean):
        print("4")

        return reIdYear, None, None,leafType(reIdYear[:, 2])
    reMat0IdYeardes = np.tile("{}>{}".format(colName[bestIndex], round(bestValue, 3)),
                                          bestreMat0IdYear.shape[0])[:, np.newaxis]
    bestreMat0IdYear2 = np.concatenate((reMat0IdYeardes, bestreMat0IdYear), axis=1)
    reMat1IdYeardes = np.tile("{}<{}".format(colName[bestIndex], round(bestValue, 3)),
                                          bestreMat1IdYear.shape[0])[:, np.newaxis]
    bestreMat1IdYear2 = np.concatenate((reMat1IdYeardes, bestreMat1IdYear), axis=1)
    reChild = pd.DataFrame(np.concatenate((bestreMat0IdYear2,bestreMat1IdYear2),axis = 0),columns=["class_{}>{}".format(colName[bestIndex],round(bestValue,3)),"id","year","ddf_{}>{}".format(colName[bestIndex],round(bestValue,3))])

    if (S - bestS) < tolS:
        print("2")
        return reIdYear, None, None,leafType(reIdYear[:, 2])
    return reChild, bestIndex, bestValue, leafType(reIdYear[:, 2])


def createTree(dataSet, leafType=regLeaf, errType=regErr, ops=(0, 1),ddfp=(2,1,1,3),colName=["colName"]):

    reChild,feat, val, meanddf = chooseBestSplit(dataSet, leafType, errType, ops,ddfp,colName)

    if feat == None:
        retlt = []
        retlt.append(reChild)
        retlt.append(meanddf)
        return retlt

    retTree = {}
    retTree['spInd'] = "{}>{}\nDDF={}".format(colName[feat],round(val,3),round(meanddf,3))
    retTree["reChild"]=reChild

    lSet, rSet = binSplitDataSet(dataSet, feat, val)
    retTree['Yes'] = createTree(lSet, leafType, errType, ops,ddfp,colName=colName)
    retTree['No'] = createTree(rSet, leafType, errType, ops,ddfp,colName=colName)
    return retTree


def panelvar(df):
    df["year2"] = (df["year"] - (df["year"].min()-1))/(df["year"] - (df["year"].min()-1)).sum()
    df["fdi"] = (df["fdi"]* df["year2"]).sum()
    df["open"] = (df["open"]* df["year2"]).sum()
    df["tech"] = (df["tech"]* df["year2"]).sum()
    df["human"] = (df["human"]* df["year2"]).sum()
    df.drop(columns = "year2",inplace = True)
    return df

if __name__ == "__main__":
    sj = pd.read_excel(r"city_inefficiency_tree.xlsx")

    sj = sj[sj.year.between(2010,2018)]
    # sj = sj[sj.id.between(1,80)]

    sj2 = sj[["id","year","Y","CO2","K","L","E","fdi","open","tech","human"]]
    sj2.head()
    sj2 = sj2.groupby("id",as_index = False).apply(panelvar)

    colName = sj2.columns

    myDat = np.mat(sj2)

    start = time.time()
    ss = createTree(myDat, ops=(0, 179),ddfp=(2,1, 1,3),colName=colName)
    end = time.time()
    print(ss)
    print("createTree, cost:", end - start, "seconds")

    import matplotlib.pyplot as plt


    decisionNode = dict(boxstyle="round4", color='r', fc='0.9')

    leafNode = dict(boxstyle="circle", color='m')

    arrow_args = dict(arrowstyle="<-", color='g')


    def plot_node(node_txt, center_point, parent_point, node_style):

        createPlot.ax1.annotate(node_txt,
                                xy=parent_point,
                                xycoords='axes fraction',
                                xytext=center_point,
                                textcoords='axes fraction',
                                va="center",
                                ha="center",
                                bbox=node_style,
                                arrowprops=arrow_args)


    def get_leafs_num(tree_dict):


        leafs_num = 0
        for key in tree_dict.keys():

            if type(tree_dict[key]).__name__ == 'dict':

                leafs_num += get_leafs_num(tree_dict[key])

        leafs_num += 1

        return leafs_num


    def get_tree_max_depth(tree_dict):


        max_depth = 0

        for key in tree_dict.keys():

            this_path_depth = 0

            if type(tree_dict[key]).__name__ == 'dict':
                 this_path_depth = 1 + get_tree_max_depth(tree_dict[key])

            else:
                 this_path_depth = 1

            if this_path_depth > max_depth:
                max_depth = this_path_depth

        return this_path_depth


    def plot_mid_text(center_point, parent_point, txt_str):

        x_mid = (parent_point[0] - center_point[0]) / 2.0 + center_point[0]
        y_mid = (parent_point[1] - center_point[1]) / 2.0 + center_point[1]
        createPlot.ax1.text(x_mid, y_mid, txt_str)
        return


    def plotTree(tree_dict, parent_point, node_txt):


        leafs_num = get_leafs_num(tree_dict)

        root = tree_dict["spInd"]

        del tree_dict['spInd']
        del tree_dict['reChild']

        center_point = (plotTree.xOff + (1.0 + float(leafs_num)) / 2.0 / plotTree.totalW, plotTree.yOff)

        plot_mid_text(center_point, parent_point, node_txt)

        plot_node(root, center_point, parent_point, decisionNode)

        plotTree.yOff = plotTree.yOff - 1.0 / plotTree.totalD

        for key in tree_dict.keys():

            if tree_dict[key] == "spInd":
                continue
            else:
                if type(tree_dict[key]).__name__ == 'dict':
                    plotTree(tree_dict[key], center_point, str(key))

                else:
                    plotTree.xOff = plotTree.xOff + 1.0 / plotTree.totalW
                    plot_node(tree_dict[key][1], (plotTree.xOff, plotTree.yOff), center_point, leafNode)
                    plot_mid_text((plotTree.xOff, plotTree.yOff), center_point, str(key))

        plotTree.yOff = plotTree.yOff + 1.0 / plotTree.totalD

        return


    def createPlot(tree_dict):


        fig = plt.figure(1, facecolor='white')

        fig.clf()
        axprops = dict(xticks=[], yticks=[])
        createPlot.ax1 = plt.subplot(111, frameon=False, **axprops)
        plotTree.totalW = float(get_leafs_num(tree_dict))
        plotTree.totalD = float(get_tree_max_depth(tree_dict))
        plotTree.xOff = -0.5 / plotTree.totalW;
        plotTree.yOff = 1.0;
        plotTree(tree_dict, (0.5, 1.0), '')

        plt.savefig(r"result\Figure 3 Efficiency tree.pdf", dpi=900, bbox_inches="tight", format="pdf")


    ss2 = copy.deepcopy(ss);
    createPlot(ss2)


    def getChildDdf(tree_dict):


        if type(tree_dict).__name__ == 'dict':
            pdF = tree_dict["reChild"]
            pdF["id"] = pdF["id"].astype(float).astype(int)

            pdF[pdF.columns[-1]] = pdF[pdF.columns[-1]].astype("float64")
            pdF = pdF.groupby([pdF.columns[0], pdF.columns[1]]).mean().reset_index()

        for key in tree_dict.keys():
            if type(tree_dict[key]).__name__ == 'dict':
                pdF = pd.merge(pdF, getChildDdf(tree_dict[key]), on=["id", ], how="left")

        return pdF

    ss1 = copy.deepcopy(ss)
    children = getChildDdf(ss1)

    fatherz = ddf(myDat, goodStart=2, goodNum=1, badNum=1, inputNum=3)
    fatherdes = np.tile("nosplit", fatherz.shape[0])[:, np.newaxis]
    fatherz = pd.DataFrame(np.concatenate((fatherdes, fatherz), axis=1), columns=["class", "id", "year", "ddf"])

    fatherz[["id", "year"]] = fatherz[["id", "year"]].astype(float).astype(int)
    fatherz["ddf"] = fatherz["ddf"].astype(float)
    fatherz = fatherz[["id", "class", "ddf"]].groupby(["id", "class"]).mean().reset_index()

    zong = pd.merge(fatherz, children, on=["id"], how="left", suffixes=("nosplit", "split"))
    zong.to_excel(r".\temp\zuihou.xlsx", index=False)


    def getChildDdf2(tree_dict):

        if type(tree_dict).__name__ == 'dict':
            pdF = tree_dict["reChild"]
            pdF[["id", "year"]] = pdF[["id", "year"]].astype(float).astype(int)

            pdF[pdF.columns[-1]] = pdF[pdF.columns[-1]].astype("float64")

        for key in tree_dict.keys():
            if type(tree_dict[key]).__name__ == 'dict':
                #             print(key)
                pdF = pd.merge(pdF, getChildDdf2(tree_dict[key]), on=["id", "year"], how="left")

        return pdF
    ss2 = copy.deepcopy(ss)
    children2 = getChildDdf2(ss2)

    fatherz2 = ddf(myDat, goodStart=2, goodNum=1, badNum=1, inputNum=3)
    fatherdes2 = np.tile("nosplit", fatherz2.shape[0])[:, np.newaxis]
    fatherz2 = pd.DataFrame(np.concatenate((fatherdes2, fatherz2), axis=1), columns=["class", "id", "year", "ddf"])

    fatherz2[["id","year"]] = fatherz2[["id", "year"]].astype(float).astype(int)

    zong2 = pd.merge(fatherz2, children2, on=["id","year"], how="left").set_index(["id","year"])
    zong2["ddf"] = zong2["ddf"].astype(float)


    zong2.reset_index().to_excel(r".\temp\zuihou2.xlsx", index=False)
    zongDropna = pd.DataFrame()
    for idN in range(1, 31):
        tep = zong2.reset_index()[zong2.reset_index()["id"] == idN].dropna(axis=1, how="all").set_index(["id", "year"])
        tep2 = tep.copy()
        for colN in range(tep.columns.shape[0]):
            if ((colN + 1) % 2 == 0) and (colN + 1) > 2:
                tep2.iloc[:, colN] = tep.iloc[:, colN - 2] - tep.iloc[:, colN]

        zongDropna = pd.concat([zongDropna, tep2], axis=0)
    zongMean = pd.DataFrame()
    for colN2 in range(0, zongDropna.columns.shape[0], 2):
        print(colN2)
        tep = zongDropna.iloc[:, colN2:colN2 + 2]
        tep2 = tep.groupby(["id", tep.columns[0]]).mean().reset_index().set_index(["id"])
        zongMean = pd.concat([zongMean, tep2], axis=1)


    zongMean.to_excel(r".\temp\gap.xlsx", index=True)