import numpy as np
from vpython import sphere, vector, rate, color, cylinder, arrow, curve, mag, cos, sin, rotate, cross, scene, canvas

#0.00001 = 0.01 밀리 테슬라
pos = 0.1 # 전기장 강도 전역변수 0.2 = 밀리 테슬라의 20000 배

scene = canvas(width=1520, height=675, center=vector(0,0,0), background=color.white)
scene.autoscale = False  # 자동 크기 조정 비활성화
scene.range = 15  # 시야 범위 설정

# 물 클래스
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
        # self.hydrogen1.pos = self.center + rotate(self.hydrogen1.pos - self.center, angle=0)
        # self.hydrogen2.pos = self.center + rotate(self.hydrogen2.pos - self.center, angle=0)
        
    def rotate(self, axis, angle):
        self.hydrogen1.pos = self.center + rotate(self.hydrogen1.pos - self.center, angle=angle, axis=axis)
        self.hydrogen2.pos = self.center + rotate(self.hydrogen2.pos - self.center, angle=angle, axis=axis)
        self.dipole = (self.oxygen.pos - (self.hydrogen1.pos + self.hydrogen2.pos) / 2).norm()

    # def attract_to_field(self, field_direction, strength=pos):
    #     self.move(strength * field_direction)
    
    def align_to_field(self, field_direction, strength=pos):
        field = (field_direction).norm()
        rotation_axis = cross(self.dipole, field)
        rotation_angle = strength * mag(rotation_axis)
        # 수소 결합 강도에 따른 회전 저항 추가, 얼음이 무극성을 띄지만, 분자 하나에 계산을 적용하는 실수 때문에 무극성의 특징이 발현되지 않음
        max_rotation = 0.05  # 최대 회전 허용 각도 (수소 결합에 의해 제한됨)
        rotation_angle = min(rotation_angle, max_rotation)
        if mag(rotation_axis) > 0:
            self.rotate(rotation_axis.norm(), rotation_angle)


    def attract_to_field(self, field_direction, strength=pos):
        self.move(strength * field_direction)
        self.align_to_field(field_direction)
        
    def add_hydrogen(self, direction):
        h_pos = self.center + direction * 0.1
        hydrogen = sphere(pos=h_pos, radius=0.1, color=color.white)
        self.hydrogens.append(hydrogen)
        bond = cylinder(pos=self.center, axis=direction*0.1, radius=0.03, color=color.white)
        self.bonds.append(bond)

def create_hexagonal_ice_layer(molecule_distance):
    molecules = []
    z = 0
    half_distance = molecule_distance * 0.5
    vertical_scale = molecule_distance * np.sqrt(3) / 2
    max_distance_squared = (1 * molecule_distance) ** 2
    rotation_offset = np.pi + 0.62

    for i in range(-5, 6):
        for j in range(-5, 6):
            x = (i + (j % 2) * half_distance)
            y = j * vertical_scale
            distance_squared = x**2 + y**2
            if 0 < distance_squared <= max_distance_squared:
                molecule = WaterMolecule(vector(x, -y, z))
                angle = np.arctan2(-y, x) + rotation_offset
                # 분자 회전 적용
                molecule.rotate(vector(0, 0, 1), angle)
                molecules.append(molecule)
                
    #수소 결합 생성
    create_hydrogen_bonds(molecules, 1)

    return molecules

# 수소 결합 함수 추가 (수소 결합을 그릴 때 사용)
def create_hydrogen_bonds(molecules, bond_distance):
    bonds = []
    for i, mol1 in enumerate(molecules):
        for j, mol2 in enumerate(molecules):
            if i != j and mag(mol1.center - mol2.center) <= bond_distance:
                bond = cylinder(pos=mol1.center, axis=mol2.center - mol1.center, radius=0.05, color=color.white)
                bonds.append(bond)
    return bonds

def maintain_hydrogen_bonds(molecules, bond_distance):
    for mol1 in molecules:
        for mol2 in molecules:
            if mol1 != mol2 and mag(mol1.center - mol2.center) <= bond_distance:
                displacement = (mol2.center - mol1.center).norm() * bond_distance
                mol2.move(displacement - (mol2.center - mol1.center))

def calculate_magnetic_field(m_pos):
    """ 자석의 전기장 벡터 계산 """
    B_north = (m_pos - north_pole.pos).norm() / mag(m_pos - north_pole.pos)**2
    B_south = (m_pos - south_pole.pos).norm() / mag(m_pos - south_pole.pos)**2
    return B_south - B_north # S극에서 나와서 N극으로 들어가는 전기장 방향
    
def update_water_molecules(molecules, north_pole, south_pole):
    for molecule in molecules:
        field = calculate_magnetic_field(molecule.center, north_pole.pos, south_pole.pos)
        molecule.attract_to_field(field)    
        
def update_ice_layer(molecules, bond_distance=1):
    for mol in molecules:
        maintain_hydrogen_bonds(molecules, 1)

def update(molecule, pos=0):
    molecule.move(vector(pos, -0.05, pos))
    molecule.attract_to_field(calculate_magnetic_field(molecule.oxygen.pos))

drag = False
pick = None

def mouse_down():
    global drag
    if scene.mouse.pick == bar_magnet:
        drag = True
    else:
        drag = False

def mouse_move():
    global drag, north_pole, south_pole, bar_magnet
    if drag:
        new_pos = scene.mouse.pos
        displacement = new_pos - bar_magnet.pos
        bar_magnet.pos += displacement
        north_pole.pos += displacement
        south_pole.pos += displacement

def mouse_release():
    global drag
    drag = False
    
    
# 마우스 이벤트 바인딩
scene.bind('mousedown', mouse_down)
scene.bind('mousemove', mouse_move)
scene.bind('mouseup', mouse_release)

# 물 분자의 초기 위치 설정
water_molecules  = [WaterMolecule(vector( 0, i * 1.0,  0)) for i in range(100)]
water_molecules2 = [WaterMolecule(vector( 1, i * 1.0,  1)) for i in range(100)]
water_molecules3 = [WaterMolecule(vector(-1, i * 1.0, -1)) for i in range(100)]

# 얼음 생성
# distance = 1
# ice_molecules = create_hexagonal_ice_layer(distance)
# hydrogen_bonds = create_hydrogen_bonds(ice_molecules, distance)

# 막대 자석 생성 (화면 오른쪽에 배치)
north_pole_pos = vector(12, pos, 0)
south_pole_pos = vector(16, pos, 0)

# 막대자석 자성 부여
bar_magnet = cylinder(pos=north_pole_pos, axis=south_pole_pos - north_pole_pos, radius=0.2, color=color.gray(0.5))
north_pole = sphere(pos=north_pole_pos, radius=0.3, color=color.blue)  # N극
south_pole = sphere(pos=south_pole_pos, radius=0.3, color=color.red)  # S극

# 전기장선 초기화
# initialize_field_lines(north_pole, south_pole) 

# 시뮬레이션 실행
while True:
    rate(60) 
    [ update(molecule ) for molecule  in water_molecules  ]
    [ update(molecule2) for molecule2 in water_molecules2 ]
    [ update(molecule3) for molecule3 in water_molecules3 ]
    # [ molecule.attract_to_field(calculate_magnetic_field(molecule.oxygen.pos)) for molecule in ice_molecules ]
    # update_ice_layer(ice_molecules)
