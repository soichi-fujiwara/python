import mojimoji
import re
import MeCab

def place_serialize(words):
  #大文字統一
  #words = words.upper()

  #英数字のみ半角統一
  words = mojimoji.zen_to_han(words, kana=False)

  #改行コード変換
  #words = words.replace("\r\n","")

  return words

def place_pickup(str_wk):
  #======================================================
  #スキップワード削除
  #======================================================
  del_word = ["<",">","＜","＞","[","]","《","》","≪","≫","【", "】"," ","　",":","：","・","弊社","駅","直結","オフィス","スキル"]
  
  #路線名パターン
  line_ptn_list = ['JR([ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+)+',
            '東武([ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+)+',
            '西武([ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+)+',
            '([ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+)+線',
            '([ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+)+鉄道',
            '([ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+)+メトロ',
            '([ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+)+ライン'
            ]

  base_word = '場所'
  place_yuragi = ["最寄駅","作業場所","勤務地"]
  
  #ゆらぎ統一
  for place in place_yuragi:
    str_wk = str_wk.replace(place,base_word)

  #余分な文章を削除
  base_word_idx = str_wk.find(base_word);
  if base_word_idx > 0:
    str_wk = str_wk[base_word_idx:base_word_idx+20]
  else:
    str_wk = ''
  
  #路線名削除
  for line in line_ptn_list:
    del_line_word = re.search(line,str_wk)
    if del_line_word != None:
      str_wk = str_wk.replace(del_line_word.group(),"")
  
  #不要文字列削除
  for word in del_word:
    str_wk = str_wk.replace(word,'')
  
  #正規化
  str_wk = place_serialize(str_wk)
    
  #======================================================
  #分かち書き
  #======================================================
  tagger = MeCab.Tagger("-Owakati")
  list_output = (tagger.parse(str_wk)).split(' ')

  #======================================================
  #「場所」に最も近い位置で書かれている数字が含まれる文節を抽出
  #======================================================
  place_str = ""
    
  if list_output.count(base_word) > 0:
    if re.search('[ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+',list_output[list_output.index(base_word)+1]) != None:
      place_str = re.search('[ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+',list_output[list_output.index(base_word)+1])
      place_str = place_str.group()

      if re.search('[ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+',list_output[list_output.index(base_word)+2]) != None:
        place_str2 = re.search('[ぁ-ゟ]+|[\ァ-ヿ]+|[一-鿐]+',list_output[list_output.index(base_word)+2])
        place_str = place_str + str(place_str2.group())
    else:
      place_str = "勤務地情報あり"
  else:
    place_str = "勤務地情報なし"
    
  return place_str
