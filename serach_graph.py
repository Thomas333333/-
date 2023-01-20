# -*- coding: UTF-8 -*-
from py2neo import NodeMatcher,Graph
graph = Graph('http://localhost:7474/', username='neo4j', password='*****')#连接neo4j
#搜索范围
type_list=['名称','发病部位','常见病因','治疗方法','临床表现','相关症状','预防措施','多发人群','就诊科室']
while(1):
    iffound = 'n'#一开始默认没有找到搜索内容
    #获取搜索范围
    type = input(' 0.名称 1.发病部位 2.常见病因 \n '+
                   '3.治疗方法 4.临床表现 5.相关症状\n'+
                  '6.预防措施 7.多发人群 8.就诊科室\n ')

    type_str = type_list[int(type)]

    text = input(f'在{type_str}模糊搜索词语:')#获取搜索词语
    # print(text)
    # query = "match (n:resource) where n.name='{0}' return n LIMIT 25".format(text)
    query = "match (n:resource) where n.{0} Contains '{1}' return n LIMIT 25".format(type_str,text)
    #生成对应的CQL查询语句 执行 cypher 语句，获得返回结果

    # print(query)
    answer = graph.run(query)

    for answer_info in iter(answer):
        print()
        if iffound != 'n':#如果找到了 就跳出循环
            break
        node_info = answer_info['n']
        for property_node in node_info.keys():
            if property_node == 'name':#排除重复属性
                continue
            print(f'{property_node}:{node_info[property_node]}') #输出该节点每个属性的值
        iffound=input('找到了吗 y or n or q\n')#获取用户反馈
    if iffound=='q':
        continue
    print('列表已穷尽，请尝试更换搜索词')
