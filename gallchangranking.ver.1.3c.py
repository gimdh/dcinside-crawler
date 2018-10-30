import requests
from bs4 import BeautifulSoup
import operator
import time
import re
import os

def request(url):
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'gall.dcinside.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }
    url_get = requests.get(url, headers=header)
    return url_get

def gall_check(minor_string, gall):
    recept = request("http://gall.dcinside.com/%sboard/lists/?id=%s" %(minor_string, gall))
    soup = BeautifulSoup(recept.text, "html.parser")
    meta_data = soup.find_all("meta", {"name": "title"})
    comp = re.findall("\"(.+갤러리)", str(meta_data))
    if comp == []:
        return None
    gall_name = comp[0]
    return gall_name


def main():
	
    is_minor = input("마이너 갤러리입니까? (y/n): ")

    if is_minor == 'y':
        minor_string = "mgallery/"
    elif is_minor == 'n': 
        minor_string = ""
    
    else:
        print("y나 n으로 입력부탁")
        main()
    
    gall = input("갤러리 id?(ex:mlp): ")
    if gall_check(minor_string, gall):
        print(gall_check(minor_string, gall))
    else:
        print("id 잘못 입력한듯")
        main()
    init_page = int(input("시작 페이지?: "))
    final_page = int(input("마지막 페이지?: "))
    nick_dic = dict()

    for page in range(init_page, final_page + 1):
        print("\rWorking page={}/{}".format(page, final_page), end="")
        recept = request("http://gall.dcinside.com/%sboard/lists/?id=%s&page=%d" %(minor_string, gall, page))
        soup = BeautifulSoup(recept.text, "html.parser")
        nick_list = soup.find_all('td', {'class': "gall_writer ub-writer"})

        for nicks in nick_list:
            try:  # 첫부분 예외처리
                nick = nicks.attrs['data-nick']
                uid = nicks.attrs['data-uid']
                ip = nicks.attrs['data-ip']
            except:
                nick = "운영자"
            if nick == "운영자":  # 공지사항
                continue
            nick_str = nick + "(" + uid + ip + ")"
            if nick_str in nick_dic:
                nick_dic[nick_str] += 1
            else:
                nick_dic[nick_str] = 1
    nick_list = dict_sorter(nick_dic)
    file_writer(gall, nick_list)    #저장


def dict_sorter(nick_dic):
    sorted_dic = sorted(nick_dic.items(), key=operator.itemgetter(1))   #딕셔너리 value로 정렬
    sorted_dic.reverse()
    return sorted_dic


def nick_change(nick_list):
    print("랭킹\t닉\t글수")
    for i in range(len(nick_list)):
        print("%d\t%s\t%s" %((i+1), nick_list[i][0], nick_list[i][1]))
    print("닉변 처리(ex)1위와 10위가 동일닉일 시 1,10 한번에 두개씩만, 종료는 0,0")
    while 1:
        change = input("닉변?: ")
        rankings = change.split(",")
        if rankings[0] == "0":
            break
        temp_1 = nick_list[int(rankings[0]) - 1][0] + "=" + nick_list[int(rankings[1]) - 1][0]
        temp_2 = nick_list[int(rankings[0]) - 1][1] + nick_list[int(rankings[1]) - 1][1]
        temp_3 = nick_list[int(rankings[1]) - 1][0]
        nick_list[int(rankings[0]) - 1] = (temp_1, temp_2)
        nick_list[int(rankings[1]) - 1] = (temp_3, 0)
    temp_dic = dict(nick_list)
    nick_list = dict_sorter(temp_dic)
    return nick_list


def file_writer(gall, nick_list):
    timestr = time.strftime("%Y_%m_%d-%H_%M")
    file_name = "%s_gall-%s.txt" %(gall, timestr)
    edit_file_name = "edit_%s_gall-%s.txt" %(gall, timestr)
    print(file_name)
    f = open(file_name, 'w', encoding = 'utf-8')
    ef = open(edit_file_name, "w", encoding = 'utf-8')
    f.write("갤창랭킹 made by hanel2527, 마이 리틀 포니 갤러리\n\n Fix by Prince \n (**마셔보세요 데자와**)\n\n")
    total = 0
    for i in range(len(nick_list)):
        total += nick_list[i][1]
    f.write("총 글수: %d\n" %total)
    f.write("랭킹\t\t닉\t\t\t\t글 수\t\t갤 지분(%)\n")

    for i in range(len(nick_list)):
        if nick_list[i][1] == 0:
            continue
        string = "%d\t\t%s\t\t\t\t%d\t\t%.2f\n" %((i+1), nick_list[i][0], nick_list[i][1], (nick_list[i][1] / total * 100))
        f.write(string)
        ef.write("%s\t%d\n" %(nick_list[i][0], nick_list[i][1]))
    f.close()
    ef.close()

def edit_nick():
    filename_list = list()
    n = 0
    for filename in os.listdir():
        if re.match("^edit_.*\.txt", filename):
            n += 1
            print(n, filename)
            filename_list.append(filename)
    num = int(input("맞는 것 번호?: "))
    file_name = filename_list[num - 1]
    print(file_name)
    f = open(file_name, "r", encoding = 'utf-8')
    nicks = f.readlines()
    nick_list = list()
    for i in range(len(nicks)):
        temp = nicks[i].split('\t')
        nick_list.append((temp[0], int(temp[1])))
    nick_list = nick_change(nick_list)
    gall = re.findall("^edit_(.*)_gall", file_name)[0]
    file_writer(gall, nick_list)
    f.close()
    original = re.findall("^edit_(.*\.txt)", file_name)[0]
    if input("원본파일 삭제?(y/n): ") == "y":
        os.remove(original)     #원본파일 삭제
        os.remove(file_name)


if __name__ == "__main__":
    print("갤창랭킹 made by hanel2527, mlp갤 \n\n 마갤 지원 패치 by Prince,  \n(**데자와는 갓음료입니다**)\n\n")
    if input("갤창랭킹/편집(g/e): ") == "g":
        main()
    edit_nick() #닉변처리
