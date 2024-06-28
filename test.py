import sys
import time
from typing import List
import random
from PIL import Image, ImageDraw

"""
Point类是数学坐标系的一个抽象的点,和Node类不是一回事
"""


class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    # 重载“==”运算符，(x1,y1)==(x2,y2)，当且仅当x1=x2，y1=y2
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y


class Map2D:
    def __init__(self, height, width) -> None:
        self.height = height
        self.width = width
        # width可以看成二维地图的行，height可以看成二维地图的列
        self.data = [["⬜" for _ in range(width)] for _ in range(height)]

    # 将地图数据用文本导出
    def show(self, file_name="output.txt") -> None:
        with open(file_name, 'w', encoding='utf-8') as file:
            for row in self.data:
                file.write(" ".join(row) + '\n')

    # 将地图数据用图片导出
    def export_image(self, file_name="map.png") -> None:
        cell_size = 10
        image = Image.new("RGB", (self.width * cell_size, self.height * cell_size), "white")
        draw = ImageDraw.Draw(image)
        for x in range(self.height):
            for y in range(self.width):
                color = "white"
                if self.data[x][y] == "⬛":
                    color = "black"
                elif self.data[x][y] == "🟥":
                    color = "red"
                elif self.data[x][y] == "🟩":
                    color = "green"
                draw.rectangle([(y * cell_size, x * cell_size), ((y + 1) * cell_size, (x + 1) * cell_size)], fill=color)
        image.save(file_name)

    # 当地图点为⬛，则为障碍物
    def set_obstacle(self, x, y):
        self.data[x][y] = "⬛"

    # 设置起点和终点
    def set_start_end(self, start: Point, end: Point) -> None:
        self.data[start.x][start.y] = "🟥"
        self.data[end.x][end.y] = "🟥"

    def obstacle_generate(self, ratio: int) -> None:
        # 随机放置障碍物
        obstacle_cells = int((self.height * self.width) * ratio)  # 障碍物占据40%的格子
        for _ in range(obstacle_cells):
            x = random.randint(0, map2d.height - 1)
            y = random.randint(0, map2d.width - 1)
            while (x == start_point.x and y == start_point.y) or (x == end_point.x and y == end_point.y) or \
                    map2d.data[x][y] == "⬛":
                x = random.randint(0, map2d.height - 1)
                y = random.randint(0, map2d.width - 1)
            map2d.set_obstacle(x, y)


"""
1.ud指的是up and down
2.rl指的是right and left
"""


class Node:
    def __init__(self, point: Point, endpoint: Point, g: float):  # 初始化中间节点的参数
        self.point = point
        self.endpoint = endpoint
        self.father = None
        self.g = g
        # h取曼哈顿距离，c=|x2-x1|+|y2-y1|
        self.h = (abs(endpoint.x - point.x) + abs(endpoint.y - point.y)) * 10
        self.f = self.g + self.h

    def get_near(self, ud, rl):  # 获取相邻节点
        near_point = Point(self.point.x + rl, self.point.y + ud)
        near_node = Node(near_point, self.endpoint, self.g + (10 if ud == 0 or rl == 0 else 14))
        return near_node


class AStar:
    def __init__(self, start: Point, end: Point, map2d: Map2D):  # 初始化A*算法的参数
        self.path = []
        self.closed_list = []
        self.open_list = []
        self.start = start
        self.end = end
        self.map2d = map2d

    # 从open_list里面找到一个代价最小的节点
    def select_current(self) -> Node:
        min_f = sys.maxsize
        node_temp = None
        for node in self.open_list:
            if node.f < min_f:
                min_f = node.f
                node_temp = node
        return node_temp

    def is_in_open_list(self, node: Node) -> bool:  # 判断节点是否在待检测队列中
        return any([open_node.point == node.point for open_node in self.open_list])

    def is_in_closed_list(self, node: Node) -> bool:  # 判断节点是否在已检测队列中
        return any([closed_node.point == node.point for closed_node in self.closed_list])

    def is_obstacle(self, node: Node) -> bool:  # 判断节点是否是障碍物
        return self.map2d.data[node.point.x][node.point.y] == "⬛"

    """
    这个函数是A*算法的核心函数，找到当前节点代价最小的邻点
    用list来当作是队列的数据结构，存放探测过或者未被探测的节点，以此来进行路径探索
    在路径探索中节点有三种状态
    状态1.加入了队列并且已经检测了，这个单独用一个Close_list队列存放
    状态2.加入了队列但是还没有检测，这个用Open_list队列存放
    状态3.还没有被加入队列
    """

    def explore_neighbors(self, current_node: Node) -> bool:
        up = (0, 1)  # 上
        down = (0, -1)  # 下
        right = (1, 0)  # 右
        left = (-1, 0)  # 左
        top_right = (1, 1)  # 右上
        top_left = (-1, 1)  # 左上
        Bottom_right = (1, -1)  # 右下
        Bottom_left = (-1, -1)  # 左下
        directions = [up, down, right, left, top_right, top_left, Bottom_right, Bottom_left]
        for direction in directions:
            ud, rl = direction
            # current_neighbor是当前节点的邻点
            current_neighbor = current_node.get_near(ud, rl)
            # 如果检测到的节点是终点，就没必要接着往下探索了，直接退出循环，结束这个函数
            if current_neighbor.point == self.end:
                return True
            # 判断一下邻点是不是已经检测或者是障碍物，如果是，就跳过这个邻点
            if self.is_in_closed_list(current_neighbor) or self.is_obstacle(current_neighbor):
                continue
            if self.is_in_open_list(current_neighbor):
                """
                作用:在open_list中找到第一个与current_neighbor相同(坐标相同)的节点
                这里有两个值得注意的点
                1.在open_list中,可能有多个与current_neighbor相同(坐标相同)的节点，
                出现这种情况是因为同一个节点，是可以通过多条不同的路径抵达的(意思就是g值不同)
                比如说节点C是当前节点,点A与节点B都能抵达节点C且g值都相同,那么节点C此时在open_list就会被添加两次

                2.previous_current_neighbor是取的在open_list中与current_neighbor相同(坐标相同)的节点中
                他们唯一的区别就是g值不同但因为有多个匹配,因此这里用next函数只取一次即可
                """

                previous_current_neighbor = next(
                    open_node for open_node in self.open_list if open_node.point == current_neighbor.point)

                """
                这时就要比较current_neighbor与previous_current_neighbor的代价了,
                假如我在本次的路径探索到的current_neighbor要比我之前的路径探索到的previous_current_neighbor的代价要小
                (这里时刻注意,current_neighbor与previous_current_neighbor是坐标相同的),那么我就要更新previous_current_neighbor的代价
                """
                if current_neighbor.f < previous_current_neighbor.f:
                    # 更新父节点
                    previous_current_neighbor.father = current_node
                    # 更新g值
                    previous_current_neighbor.g = current_neighbor.g
            else:
                # 对应状态3，直接入队
                current_neighbor.father = current_node
                self.open_list.append(current_neighbor)
        return False

    def find_path(self):
        start_node = Node(point=self.start, endpoint=self.end, g=0)
        self.open_list.append(start_node)
        while True:
            # 从open_list里面取出一个代价值最小节点
            current_node = self.select_current()
            if current_node is None:
                return None
            # 取出来后，从open_list里面删除，添加到closed_list里面
            self.open_list.remove(current_node)
            self.closed_list.append(current_node)
            # 当current_node是终点时，explore_neighbors函数会返回一个True
            if current_node.point == self.end or self.explore_neighbors(current_node):
                while current_node.father is not None:
                    self.path.insert(0, current_node.point)
                    # 这里其实就是相当于遍历一个链表
                    current_node = current_node.father
                return self.path


if __name__ == "__main__":
    # 创建地图
    map2d = Map2D(20, 20)
    # 设置起点和终点
    start_point = Point(1, 3)
    end_point = Point(6, 15)
    map2d.set_start_end(start_point, end_point)
    map2d.obstacle_generate(0.3)
    # 运行A*算法
    start_time = time.time()
    a_star = AStar(start_point, end_point, map2d)
    path = a_star.find_path()
    end_time = time.time()
    # 打印结果
    if path:
        print("找到最佳路径：")
        for point in path:
            map2d.data[point.x][point.y] = "🟩"
    else:
        print("未找到路径！")
    map2d.export_image("result.png")
    # map2d.show()
    # 打印运行时间
    print("程序运行时间：", end_time - start_time, "秒")

