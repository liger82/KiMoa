from flask import Flask, request
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
from recomm import recomSystem
import time
connection = MongoClient("mongodb://master:master1@ds147746.mlab.com:47746/app_7")    #mongodb 주소 입력
db = connection['app_7']             #mongodb database 입력
userCollection = db['users']             #collection입력
recordCollection = db['records']
# 추후 추가할 예정
# interestCollection = db['interest']

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

def getUser(uuid):
    """
    DB에 있는 User collection중 uuid와 맞는 데이터 가져옴
    """
    user = userCollection.find({
        "uuid": uuid
    })
    return user

def getUserId():
    """
        DB에 있는 User collection 가져옴
    """
    # print("어디가 문제야2")
    return userCollection.find()

def getRecordTid(uuid):
    """
        DB에 있는 record Usercollection 가져옴(최근 50개)
    """
    # print("어디가 문제야3-1")
    records = recordCollection.find({
        "uuid": uuid
    })
    result = []
    records = list(records)

    # print("어디가 문제야3-2")

    return records

def countlist(list):
    # print("어디가 문제야4")
    dic = {}

    if len(list) is 0:
        return dic
    for i in list:
        if i not in dic:
            dic[i] = 1
        else:
            dic[i] += 1
    return dic

def mergeUser(uuid):
    """
    User ID와 record 목록을 가져와서 필요한 데이터 셋으로 합침
    """
    # print("어디가 문제야5")
    user = getUser(uuid)
    user = list(user)
    user = user[0]
    records = getRecordTid(uuid)
    listr = []
    for r in records:
        listr.append(r['tid'])
    resultlist = []
    result = {}
    dicts = {}

    # user 행위 데이터가 없으면 관심리스트의 내용을 넣는다.
    if len(records) is 0:
        dicts = countlist(user['likes'])
    else: # user 행위 데이터가 있으면 행위 데이터와 관심리스트를 합쳐서 넣는다.
        dicts = countlist(listr+user['likes'])

    kk = list(dicts.keys())

    for key in kk:
        result = {}
        result['uuid'] = uuid
        result['tid'] = key
        result['count'] = dicts[key]
        resultlist.append(result)

    return resultlist

def startUser(uuid):
    """
    유저가 처음 시작유저인지 판단
    """
    # print("어디가 문제야6")
    if getRecordTid(uuid):
        return False
    else:
        return True

# 추후 추가할 예정
# def getNotInterested(uuid):
#     """
#     notInterested 가져옴
#     """
#     # print("어디가 문제야7")
#     interest = interestCollection.find({
#         'uuid': uuid
#     })
#     return interest

class UserData(object):
    """
    해당 클래스는 받아온 유저 데이터를 리스트에 저장하기 위한 목적으로 resultArr에 저장
    makeUserList()는 resultArr을 갱신하는 함수(정기적으로)
    """
    def __init__(self):
        self.resultArr = []

    def recommUpdate(self):
        """
        데이터 값 받아서 리스트로 만들어줌
        """
        # print("어디가 문제야8")
        start_vect = time.time()
        print("시작합니다")
        for ii in getUserId():
            uid = ii['uuid']
            user = mergeUser(uid)
            for u in user:
                temp = []
                temp.append(u['uuid'])
                temp.append(u['tid'])
                temp.append(u['count'])
                self.resultArr.append(temp)

        # 추천 목록 업데이트
        rs = recomSystem(self.resultArr)
        rs.convertDataFromDB()
        topN = rs.topNprocess()
        # print("test 2")
        print(rs.recommendItemByUserSim(topN,'uuid0002'))

        # 각 uuid마다 추천해서 나온 목록을 user table의 recommends에 넣어준다.
        for iii in getUserId():
            uid = iii['uuid']
            recommendList = rs.recommendItemByUserSim(topN, uid)  # 여기에 넣어주세요 추천매장목록
            query = {"uuid": uid}
            newvalue = {"$set": {"recommends": recommendList}}
            userCollection.update_one(query, newvalue)

        print("끝")
        print("training Runtime: %0.2f Minutes" % ((time.time() - start_vect) / 60))

UD = UserData()

scheduler = BackgroundScheduler()
UD.recommUpdate()
scheduler.add_job(func=UD.recommUpdate, trigger="interval", seconds=3600)  # seconds로 분기 시간을 조정할 수 있음
scheduler.start()

#
# @app.route('/recommand', methods=["GET"])
# def recommand():
#     return "dd"

if __name__ == '__main__':
    print("Starting webapp...")
    app.run("192.168.0.83:5000")