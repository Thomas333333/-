import os
import json
import copy
from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher


class KG:

    def __init__(self):
        self.graph = Graph('http://localhost:7474/', username='neo4j', password='kgneo4j')
        self.dir_path='D:\Download\KGdata\wiki-covid-19.json'

    def read_json(self):
        jsonfile = open(self.dir_path, 'r', encoding="utf-8")
        jsondata = json.load(jsonfile)
        data=jsondata['@graph']

        class_value={}  # id与类名的映射
        subclass={}  # 类与父类的映射
        property_value = {}  # id与属性值的映射
        resources_value = {}  # id与资源名的映射
        resources_type = {}   # id 与类型的映射
        resources_text = {}  # 每个资源下的 文字属性  以 dict(list(dict()))形式给出
        resources_connection = {}  # 资源之间的相互连接  以dict(dict(list()))形式给出

        data_class=data[0:49]
        for dataclass in data_class:
            class_value[dataclass['@id']]=dataclass['label']['@value']
            if 'subClassOf'in dataclass.keys():
                subclass[dataclass['@id']]=dataclass['subClassOf']
        # print(class_value)
        # print(subclass)


        data_property = data[49:139]
        for dataproperty in data_property:
            property_value[dataproperty['@id']]=dataproperty['label']['@value']
        # print(property_value)


        data_resource = data[139:]
        for dataresource in data_resource:
            resources_value[dataresource['@id']]=dataresource['label']['@value']
            resources_type[dataresource['@id']] = dataresource['@type']
            # print(list(dataresource.keys())[3:])
            # print(dataresource.keys())
            property_of_resource = list(dataresource.keys())[3:]
            text = []
            connection={}
            for p in property_of_resource:
                temp=dataresource[p]
                if temp.split('/')[0]!='http:':
                    textdict = {}
                    textdict[p] = dataresource[p]
                    text.append(textdict)
                else:
                    temp2=temp.split(',')
                    connection[p]= copy.deepcopy(temp2)
            if  connection :
                resources_connection[dataresource['@id']] = copy.deepcopy(connection)
            resources_text[dataresource['@id']] = copy.deepcopy(text)

        # print(resources_value)
        return class_value,subclass,property_value,resources_value,resources_type,resources_text,resources_connection

    def create_node(self,label,name):#自己写的
        Nodetocreate = Node(label, name=name)
        self.graph.create(Nodetocreate)

        return Nodetocreate

    # def create_node2(self, label, name):#测试时避免重复
    #     n = "_.name=" + "\"" + name + "\""
    #     matcher = NodeMatcher(self.graph)
    #     # 查询是否已经存在，若存在则返回节点，否则返回None
    #     value = matcher.match(label).where(n).first()
    #     # 如果要创建的节点不存在则创建
    #     if value is None:
    #         node = Node(label, name=name)
    #         n = self.graph.create(node)
    #         return n
    #     print('exist')
    #     return None


    def get_All_Nodes(self,class_value,resources_value):
        class_nodes={}
        resource_nodes={}
        for classid in class_value.keys():
            # class_nodes[classid]=copy.deepcopy(self.create_node('class',class_value[classid]))
            class_nodes[classid]=self.create_node('class',class_value[classid])
            print(classid)

        for resourceid in list(resources_value.keys()):
        # for resourceid in resources_value.keys()[0:100]:
            # resource_nodes[resourceid]=copy.deepcopy(self.create_node('resource',resources_value[resourceid]))
            resource_nodes[resourceid]=self.create_node('resource',resources_value[resourceid])
            print(resourceid)

        return class_nodes,resource_nodes

    def make_connection(self,node1,property,node2):
        relation = Relationship(node1,property,node2)
        self.graph.create(relation)

    def createKG(self):

        class_value, subclass, property_value, resources_value, resources_type, resources_text, resources_connection=\
            self.read_json()
        class_nodes, resource_nodes=self.get_All_Nodes(class_value,resources_value) #获取所有节点  目前只取了少量数据

        #创建子类的边
        for classid in subclass.keys():
            self.make_connection(class_nodes[classid],'属于',class_nodes[subclass[classid]])

        #资源归类
        ###
        for resourcesid in list(resources_type.keys()):
            self.make_connection(resource_nodes[resourcesid],'属于',class_nodes[resources_type[resourcesid]])
        # print(class_nodes)

        #资源节点之间互相连接
        ###
        for resourcesid in list(resources_connection.keys()):
            id_connection=resources_connection[resourcesid]
            for p in id_connection.keys():
                completed_p='http://www.openkg.cn/COVID-19/wiki/property/'+p
                propertytext=property_value[completed_p]
                # print(propertytext)
                # print(id_connection[p])
                connected_nodes=id_connection[p]
                for rid in connected_nodes:
                    self.make_connection(resource_nodes[resourcesid],propertytext,resource_nodes[rid])

        #给资源节点添加属性

        for resourcesid in list(resources_text.keys()):
            process_list = resources_text[resourcesid]
            for textdict in process_list:
                for p in textdict.keys():
                    completed_p='http://www.openkg.cn/COVID-19/wiki/property/'+p
                    propertytext = property_value[completed_p]
                    resource_nodes[resourcesid].update({propertytext:textdict[p]})
            self.graph.push(resource_nodes[resourcesid])



















# Nodes={}
# a = Node('class',name='i')
# Nodes['5']=copy.deepcopy(a)
# Person2 = Node('人', name='何姜杉')
# Person2['大哥'] = 20
# graph.create(Person2)  # 创建结点
# Person3 = Node('人', name='冯亮文')
# graph.create(Person3)  # 创建结点
# relation1 = Relationship(Person1,'的叠是',Person2)
# graph.create(relation1)  # 创建关系
#
# relation2 = Relationship(Person1,'的叠是',Person3)
# graph.create(relation2)  # 创建关系

covidKG=KG()
covidKG.createKG()