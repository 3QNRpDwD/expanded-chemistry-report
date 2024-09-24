import numpy as np
from vpython import sphere, vector, rate, color, cylinder, arrow, curve, mag, cos, sin, rotate, cross

pos = 0.2 # 자기장 강도 전역변수

# 물 분자를 나타내는 클래스
class WaterMolecule:
    def __init__(self, position):
        self.center = position
        # 산소(O) 원자 (빨간색)
        self.oxygen = sphere(pos=position, radius=0.3, color=color.red)
        
        # 수소(H) 원자 (파란색)
        self.hydrogen1 = sphere(pos=position + vector(0.4, 0.2, 0), radius=0.2, color=color.blue)
        self.hydrogen2 = sphere(pos=position + vector(-0.4, 0.2, 0), radius=0.2, color=color.blue)
        
        self.dipole = (self.oxygen.pos - (self.hydrogen1.pos + self.hydrogen2.pos) / 2).norm()

    def move(self, direction):
        self.center += direction
        self.oxygen.pos += direction
        self.hydrogen1.pos += direction
        self.hydrogen2.pos += direction
        
    def rotate(self, axis, angle):
        self.hydrogen1.pos = self.center + rotate(self.hydrogen1.pos - self.center, angle=angle, axis=axis)
        self.hydrogen2.pos = self.center + rotate(self.hydrogen2.pos - self.center, angle=angle, axis=axis)
        self.dipole = (self.oxygen.pos - (self.hydrogen1.pos + self.hydrogen2.pos) / 2).norm()

    # def attract_to_field(self, field_direction, strength=pos):
    #     """ 물 분자를 자기장 방향으로 이동"""
    #     self.move(strength * field_direction)
    def align_to_field(self, field_direction, strength=0.1):
        field = (field_direction).norm()
        rotation_axis = cross(self.dipole, field)
        rotation_angle = strength * mag(rotation_axis)
        if mag(rotation_axis) > 0:
            self.rotate(rotation_axis.norm(), rotation_angle)

    def attract_to_field(self, field_direction, strength=0.2):
        self.move(strength * field_direction)
        self.align_to_field(field_direction)

def calculate_magnetic_field(m_pos):
    """ 자석의 자기장 벡터 계산 """
    B_north = (m_pos - north_pole.pos).norm() / mag(m_pos - north_pole.pos)**2
    B_south = (m_pos - south_pole.pos).norm() / mag(m_pos - south_pole.pos)**2
    return B_south - B_north # S극에서 나와서 N극으로 들어가는 자기장 방향

# def calculate_magnetic_field(pos, north_pos, south_pos, strength=pos):
#     """자석의 자기장 벡터 계산"""
#     r_n = pos - north_pos
#     r_s = pos - south_pos
#     B_n = strength * r_n / np.linalg.norm(r_n)**3
#     B_s = -strength * r_s / np.linalg.norm(r_s)**3
#     return B_n + B_s

# 곡선 자기장 선 생성
def create_field_lines(north_pos, south_pos, num_lines=20, num_points=100, max_length=100):
    """자기장선 생성"""
    lines = []
    
    # 시작점 설정 (N극 주변에 원형으로 배치)
    from math import cos, sin, pi
    start_radius = 1  # 시작 반경
    for i in range(num_lines):
        angle = 2 * pi * i / num_lines
        start = north_pos + vector(start_radius*cos(angle), start_radius*sin(angle), 0)
        line = [start]
        
        for _ in range(num_points):
            m_pos = line[-1]
            if mag(m_pos - south_pos) < 0.1:  # S극에 도달하면 중단
                break
            B = calculate_magnetic_field(m_pos)
            next_pos = m_pos + B.norm() * 0.1  # 자기장 방향으로 이동 (크기 정규화)
            line.append(next_pos)
            
            if mag(next_pos - north_pos) > max_length:  # 최대 길이 제한
                break
        
        lines.append(line)
    
    return lines    

def update_field_lines(curves, lines):
    """자기장선 업데이트"""
    for curve, line in zip(curves, lines):
        curve.clear()
        for point in line:
            curve.append(pos=point)

# 자기장선 초기화 (시뮬레이션 시작 시 호출)
def initialize_field_lines(north_pole, south_pole):
    global field_lines, curves
    field_lines = create_field_lines(north_pole.pos, south_pole.pos)
    curves = [curve(pos=line, radius=0.02, color=color.cyan) for line in field_lines]

# 시뮬레이션 루프에서 호출
# def update_magnetic_field(north_pole, south_pole):
#     global field_lines, curves
#     field_lines = create_field_lines(north_pole.pos, south_pole.pos)
#     update_field_lines(curves, field_lines)
def update_water_molecules(molecules, north_pole, south_pole):
    for molecule in molecules:
        field = calculate_magnetic_field(molecule.center, north_pole.pos, south_pole.pos)
        molecule.attract_to_field(field)

# 시뮬레이션 루프에서 호출
def update_magnetic_field():
    global field_lines, curves
    field_lines = create_field_lines(north_pole.pos, south_pole.pos)
    update_field_lines(curves, field_lines)
    
def update(molecule, pos=0):
    molecule.move(vector(pos, -0.05, pos))
    molecule.attract_to_field(calculate_magnetic_field(molecule.oxygen.pos))

# 곡선 형태의 자기장 선 생성
num_lines = 12  # 그릴 자기장 선의 개수
num_points = 50  # 각 선에 대한 점의 개수
curves = []

# 물 분자의 초기 위치 설정
water_molecules  = [WaterMolecule(vector( 0, i * 1.0,  0)) for i in range(30)]
water_molecules2 = [WaterMolecule(vector( 1, i * 1.0,  1)) for i in range(30)]
water_molecules3 = [WaterMolecule(vector(-1, i * 1.0, -1)) for i in range(30)]

# 막대 자석 생성 (화면 오른쪽에 배치)
north_pole_pos = vector(5, pos, 0)
south_pole_pos = vector(9, pos, 0)

# 막대자석 생성
bar_magnet = cylinder(pos=north_pole_pos, axis=south_pole_pos - north_pole_pos, radius=0.2, color=color.gray(0.5))
north_pole = sphere(pos=north_pole_pos, radius=0.3, color=color.red)  # N극
south_pole = sphere(pos=south_pole_pos, radius=0.3, color=color.blue)  # S극

# 자기장선 초기화
initialize_field_lines(north_pole, south_pole) 

# 시뮬레이션 실행
while True:
    rate(20) 
    [ update(molecule ) for molecule  in water_molecules  ]
    [ update(molecule2) for molecule2 in water_molecules2 ]
    [ update(molecule3) for molecule3 in water_molecules3 ]
    # update_magnetic_field()
