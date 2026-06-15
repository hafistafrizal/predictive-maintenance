class ProfileKendaraan:
    def __init__(self, nama, idle_rpm, max_torque, max_rpm, id=None):
        self.id = id
        self.nama = nama
        self.idle_rpm = idle_rpm
        self.max_torque = max_torque
        self.max_rpm = max_rpm
