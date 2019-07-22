import re
import mojimoji

def tanka_serialize(words):
    #大文字統一
    words = words.upper()

    #英数字のみ半角統一
    words = mojimoji.zen_to_han(words, kana=False)
      
    #電話番号削除
    #(稼働時間と形式が重複する為)
    if len(re.findall('[0-9]{3}-[0-9]{4}-[0-9]{4}',words)) > 0:
      tel_list = re.findall('[0-9]{3}-[0-9]{4}-[0-9]{4}',words)
      if len(tel_list) > 0:
        for tel in tel_list:
          words = words.replace(tel,'')

    #チルダ統一1
    ser_word = ["〜","～", "-","－","から","MAX"]
    for word in ser_word:
      words = words.replace(word,"~")
      
    #稼働時間削除
    if len(re.findall('[0-9]{3}H~[0-9]{3}H',words)) > 0:
      kado = re.findall('[0-9]{3}H~[0-9]{3}H',words)[0]
      words = words.replace(kado,"")
    if len(re.findall('[0-9]{3}~[0-9]{3}H',words)) > 0:
      kado = re.findall('[0-9]{3}~[0-9]{3}H',words)[0]
      words = words.replace(kado,"")
    if len(re.findall('[0-9]{3}~[0-9]{3}',words)) > 0:
      kado = re.findall('[0-9]{3}~[0-9]{3}',words)[0]
      words = words.replace(kado,"")
      
    #スキル見合い
    ser_word = ["スキル見合い","スキル見合","ご相談","相談","ご提示下さい","ご提示ください","スキルにより相談"]
    for word in ser_word:
      words = words.replace(word,"")
      
    #曖昧単価加工
    if len(re.findall('[0-9]{1}・',words)) > 0:
      aimai = re.findall('[0-9]{1}・',words)[0]
      words = words.replace(aimai,"")
    if len(re.findall('[0-9]{1}･',words)) > 0:
      aimai = re.findall('[0-9]{1}･',words)[0]
      words = words.replace(aimai,"")
    if len(re.findall('[0-9]{1}、',words)) > 0:
      aimai = re.findall('[0-9]{1}、',words)[0]
      words = words.replace(aimai,"")
      
    #改行コード変換
    words = words.replace("\r\n","")

    #小数点無効
    words = words.replace(".0","")

    #万円単位変換
    words = words.replace("0000","")
    
    #範囲指定正規化(「まで」表現置換)
    #search(最初の一致文字列の数値のみを返す)
    if re.search('[0-9]{2}まで',words):
      made_val = re.sub(r'\D', '',re.search('[0-9]{2}まで',words).group())
      words = words.replace(made_val+'まで','~'+made_val)
      
    return words
 
import MeCab

def tanka_pickup(str_wk):
  #======================================================
  #スキップワード削除
  #======================================================
  del_word = ["<",">","＜","＞","[","]","《","》","≪","≫","【", "】"," ","　",":","：","完全","位","くらい","ぐらい","およそ","大体","だいたい","約","前後","円","万","下さい","ください","※"]
  
  base_word = '単価'
  tanka_yuragi = ["予算単価","単金","金額","価格","月額","予算","条件"]

  #ストップワード削除
  for word in del_word:
    str_wk = str_wk.replace(word,'')

  #ゆらぎ統一
  for tanka in tanka_yuragi:
    str_wk = str_wk.replace(tanka,base_word)

  #正規化
  str_wk = tanka_serialize(str_wk)

  #======================================================
  #分かち書き
  #======================================================
  tagger = MeCab.Tagger("-Owakati")
  list_output = (tagger.parse(str_wk)).split(' ')

  #======================================================
  #「単価」に近い位置で書かれている数字が含まれる文節を抽出
  #======================================================
  tanka_str = ""

  #範囲指定
  if list_output.count(base_word) == 1:
    if list_output[list_output.index(base_word)+1] == "~":
      tanka_str = "00~" + list_output[list_output.index(base_word)+2]
    
  if list_output.count(base_word) > 0:
    #ひらがな、カタカナ、漢字でなければ単価情報があると判断
    if re.search('[ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+',list_output[list_output.index(base_word)+1]) is None:
      if list_output[list_output.index(base_word)+1].isdecimal() is True or list_output[list_output.index(base_word)+2].isdecimal() is True or list_output[list_output.index(base_word)+3].isdecimal() is True:
        tanka_str = list_output[list_output.index(base_word)+1] + list_output[list_output.index(base_word)+2] + list_output[list_output.index(base_word)+3]
      else:
        tanka_str = "単価情報あり"
    else:
      tanka_str = "単価完全なし"
    
  return tanka_str 

import pandas as pd

def tanka_output(pickup_str): 

  #======================================================
  #範囲指定単価(exp:A～B)(2桁～2桁) 編集
  #======================================================
  tanka_range = re.findall('[0-9]{2}~[0-9]{2}',pickup_str)

  #下限算出
  if len(tanka_range) == 1:
  min_tanka = int(tanka_range[0].split('~')[0])
  else:
  min_tanka = 0

  #上限算出
  if len(tanka_range) == 1:
  max_tanka = int(tanka_range[0].split('~')[1])
  else:
  max_tanka = 0

  #======================================================
  #範囲指定単価(exp:A～B)(2桁～3桁) 編集
  #======================================================
  if min_tanka > max_tanka:
  tanka_range = re.findall('[0-9]{2}~[0-9]{3}',pickup_str)

  #下限算出
  if len(tanka_range) == 1:
  min_tanka = int(tanka_range[0].split('~')[0])
  else:
  min_tanka = 0

  #上限算出
  if len(tanka_range) == 1:
  max_tanka = int(tanka_range[0].split('~')[1])
  else:
  max_tanka = 0

  #======================================================
  #上限指定単価(exp:～A) 編集
  #======================================================
  if min_tanka == 0 and max_tanka == 0:
  tanka_range = re.findall('~[0-9]{2}',pickup_str)

  #下限算出
  min_tanka = 0

  #上限算出
  if len(tanka_range) == 1:
  max_tanka = pickup_str.replace("~","") 
  #数値のみ抽出
  max_tanka = re.sub(r'\D', '',max_tanka)

  #======================================================
  #単価単独指定(exp:A) 編集
  #======================================================
  if min_tanka == 0 and max_tanka == 0:
  tanka_range = re.findall('[0-9]{2}',pickup_str)

  #下限算出
  if len(tanka_range) == 1:
  #数値のみ抽出
  min_tanka = re.sub(r'\D', '',tanka_range[0])

  #上限算出
  if len(tanka_range) == 1:
  #数値のみ抽出
  max_tanka = re.sub(r'\D', '',tanka_range[0])

  #======================================================
  #下限指定(exp:A以上) 編集
  #======================================================
  tanka_range = re.findall('[0-9]{2}以上',pickup_str)

  #下限算出
  if len(tanka_range) == 1:
  #数値のみ抽出
  min_tanka = re.sub(r'\D', '',tanka_range[0])
  max_tanka = 99

  #======================================================
  #下限指定(exp:A~) 編集
  #======================================================
  if min_tanka == max_tanka:
  tanka_range = re.findall('[0-9]{2}~',pickup_str)

  #下限算出
  if len(tanka_range) == 1:
  #数値のみ抽出
  min_tanka = re.sub(r'\D', '',tanka_range[0])
  max_tanka = 99

  #print(str(index) + ":" + pickup_str +"|MIN:" + str(min_tanka) + "|" + "MAX:" + str(max_tanka))
  ret_word = "MIN:" + str(min_tanka) + "|" + "MAX:" + str(max_tanka)
  return ret_word
