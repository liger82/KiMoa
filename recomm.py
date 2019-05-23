import surprise
import pandas as pd
from collections import defaultdict
from surprise import SVD

class recomSystem:
    def __init__(self, inputData):
        # Reader
        self.reader = surprise.Reader()
        self.inputData = inputData
        self.data = []

    # 전체 계산해서 각 유저에 대한 추천 item(tid)을 defaultdict 형식으로 반환
    def get_top_n(self,predictions, n=5):
        '''Return the top-N recommendation for each user from a set of predictions.

        Args:
            predictions(list of Prediction objects): The list of predictions, as
                returned by the test method of an algorithm.
            n(int): The number of recommendation to output for each user. Default
                is 10.

        Returns:
        A dict where keys are user (raw) ids and values are lists of tuples:
            [(raw item id, rating estimation), ...] of size n.
        '''

        # First map the predictions to each user.
        # 각 user에 대한 예측치 담기
        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_n[uid].append((iid, est))

        # Then sort the predictions for each user and retrieve the k highest ones.
        # 각 유저에 대한 예측치를 정렬하고 가장 가까운 K개를 담는다.
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n

    # 데이터 읽어오기
    def convertDataFromDB(self):
        df = pd.DataFrame(self.inputData)
        spdata = surprise.Dataset.load_from_df(df, self.reader)
        self.data = spdata.build_full_trainset()

    # 데이터 처리해서
    def topNprocess(self):
        algo = SVD()
        algo.fit(self.data)
        testset = self.data.build_anti_testset()
        predictions = algo.test(testset)
        return self.get_top_n(predictions)

    # 사용자 간 유사도를 기반으로 한명의 유저에게 추천할 tid list 반환
    def recommendItemByUserSim(self,top_n, uid):
        return [tid for (tid, _) in top_n[uid]]
