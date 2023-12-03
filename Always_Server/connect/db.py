import pymongo


mart_dic = {'shin_ramyun': '신 라면', 'jin_ramyun': '진 라면', 'chapagetti': '짜 파게티', 'paldo_bibim_noodle': '팔도 비빔면', 'anseongtang_noodle': '안성탕면',
            'coca_cola': '코카 콜라', 'chilsung_cider': '칠성 사이다', 'fanta': '환  타', 'mogumogu': '모구모구', 'milkis': '밀 키스',
            'shrimp_cracker': '새우 깡', 'poca_chip': '포카 칩', 'honey_butter_chip': '허니 버터칩', 'home_run_ball': '홈런 볼', 'cheetos': '치 토스',
            'tylenol': '타이레놀, 해열 진통제', 'artec': '아르텍, 알레르기 약', 'aspirin': '아스피린, 심장마비 예방 약', 'actifed': '액티피드, 종합 감기 약', 'doctorbearse': '베아제, 소화제',
            'person': '백 원', '500won': '오백 원', '1000won': '천 원', '5000won': '오천 원', '10000won': '만 원', '50000won': '오만 원', 'medicine_box': '약통'}

conn = pymongo.MongoClient('192.168.10.189', 27017)
always = conn.always
dataset = always.dataset
dataset.insert_one({"id": "1", "pick": "", "goods": "mart_dic", "flag": False})
