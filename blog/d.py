def add_dictionary(*tokenized_list):
        origin_df = 1
        try:
            origin_df = pd.read_csv("C:\\mecab\\user-dic\\intake_dic.csv", encoding='utf-8', header=None)
        except:
            print('No default intake_dic')
        keyword_list = []   
        for i in tokenized_list:
            if type(i) == list:
                for j in i:
                    j = j.split('_')
                    temp = [j[0],'' ,'' ,'' ,j[1],'',j[2], j[3],'*','*','*','*']
                    keyword_list.append(temp)
            else:
                i = i.split('_')
                temp = [i[0],'','','',i[1],'',i[2], i[3], '*','*','*','*']
                keyword_list.append(temp)


        keyword_df = pd.DataFrame(keyword_list)
        print(type(origin_df))
        if type(origin_df) != int:
            keyword_df = pd.concat((origin_df, keyword_df), ignore_index=True)
        else: 
            print('a')
            pass
        print(keyword_df.shape)

        keyword_df.to_csv("C:\\mecab\\user-dic\\intake_dic.csv", encoding='utf-8',index=None, header=False)   
