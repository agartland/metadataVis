#!/usr/bin/env python

import pandas as pd
import numpy as np
import argparse

def generateData(Nptids, Nfeat, Npmd=5, Nmmd=5):
    ptidInd = ['P%d' % (i) for i in range(Nptids)]
    featInd = ['F%d' % (i) for i in range(Nfeat)]

    mu = np.random.rand(Nfeat) * 10
    sigma2 = np.random.rand(Nfeat) * 3

    base = np.random.randn(Nptids, Nfeat)

    for i, mu_i, sigma2_i in zip(range(mu.shape[0]), mu, sigma2):
        base[:, i] = (base[:, i] * sigma2_i) * mu_i

    """Create meta-data for each PTID"""
    pmd_range = range(1, Npmd)
    ptidMD = pd.DataFrame(np.random.randn(Nptids) * 10 + 50, index=ptidInd, columns=['1'])
    ptidMD.index.name = 'PtID'
    for i in pmd_range:
        ptidMD.loc[:, i] = np.random.randn(Nptids) * 100

    """Create meta-data for each measurment"""
    mmd_range = range(1, Nmmd)
    mMD = pd.DataFrame(np.random.randn(Nfeat) * 10 + 50, index=featInd, columns=['1'])
    mMD.index.name = 'Feature'
    for i in mmd_range:
        mMD.loc[:, i] = np.random.randn(Nfeat) * 100

    baseDf = pd.DataFrame(base, columns=featInd, index=ptidInd)
    baseDf.index.name = 'PtID'

    return baseDf, ptidMD, mMD

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Program to generate fake data.')
    parser.add_argument('--Nptids', type=int, default=100,
                        help='Number of PTIDs in the dataset')

    args = parser.parse_args()

    baseDf, ptidMD, mMD = generateData(Nptids=args.Nptids, Nfeat=50, Npmd=5, Nmmd=5)

    baseDf.to_csv('base_data.csv')
    ptidMD.to_csv('ptid_metadata.csv')
    mMD.to_csv('measures_metadata.csv')


