from typing import List, Dict
from enum import Enum
import random
from datetime import datetime


# Define device type and firmware version to risk level mapping
DEVICE_RISK_LEVELS = {
    "smart_light": {"1.0": 5, "1.1": 3, "1.2": 2},
    "thermostat": {"1.0": 4, "1.1": 3, "1.2": 1},
    "security_camera": {"1.0": 6, "1.1": 4, "1.2": 3},
    "door_lock": {"1.0": 7, "1.1": 5, "1.2": 3}
}

# Define device status
class DeviceStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_MAINTENANCE = "under maintenance"


# Define user roles
class Role(Enum):
    VIEWER = "viewer"
    MANAGER = "manager"
    ADMIN = "admin"  # Added Admin role for more complex permissions


# Define the user class
class User:
    def __init__(self, username: str, role: Role, is_active: bool = True):
        self.username = username
        self.role = role
        self.is_active = is_active

    def __str__(self):
        return f"{self.username} ({self.role.value}) - {'Active' if self.is_active else 'Inactive'}"


# Define the IoT device class
class IoTDevice:
    def __init__(self, device_id: str, device_type: str, firmware_version: str, status: DeviceStatus = DeviceStatus.ACTIVE):
        self.device_id = device_id
        self.device_type = device_type
        self.firmware_version = firmware_version
        self.status = status
        self.last_updated = datetime.now()  # Store the last updated time
        self.risk_level = self.calculate_risk()

    def calculate_risk(self) -> int:
        """Calculate the risk level of the device based on type, firmware version, and other factors."""
        base_risk = DEVICE_RISK_LEVELS.get(self.device_type, {}).get(self.firmware_version, 0)
       
        # Add dynamic risk adjustment based on age of firmware
        firmware_age_days = (datetime.now() - self.last_updated).days
        if firmware_age_days > 180:  # If firmware hasn't been updated in over 6 months
            base_risk += 2
       
        # Add random risk factor for unpredictability (could be based on vulnerabilities or environmental factors)
        base_risk += random.randint(0, 2)
       
        return base_risk

    def __str__(self):
        return f"Device {self.device_id}: {self.device_type} v{self.firmware_version} - Status: {self.status.value} - Risk Level: {self.risk_level}"


# Define the Recommendation class to handle adding and approval of recommendations
class Recommendation:
    def __init__(self, description: str, approved: bool = False):
        self.description = description
        self.approved = approved

    def approve(self):
        self.approved = True

    def reject(self):
        self.approved = False

    def __str__(self):
        return f"Recommendation: {self.description} - {'Approved' if self.approved else 'Pending'}"


# Define the DeviceReport class to manage the risk report
class DeviceReport:
    def __init__(self):
        self.devices: List[IoTDevice] = []
        self.recommendations: List[Recommendation] = []

    def add_device(self, device: IoTDevice):
        self.devices.append(device)

    def generate_report(self) -> str:
        report = "\n".join(str(device) for device in self.devices)
        return report

    def add_recommendation(self, recommendation: Recommendation):
        self.recommendations.append(recommendation)

    def view_recommendations(self) -> str:
        return "\n".join(str(rec) for rec in self.recommendations)

    def generate_statistics(self) -> str:
        """Generate advanced statistics for the report."""
        total_devices = len(self.devices)
        active_devices = len([d for d in self.devices if d.status == DeviceStatus.ACTIVE])
        inactive_devices = len([d for d in self.devices if d.status == DeviceStatus.INACTIVE])
        maintenance_devices = len([d for d in self.devices if d.status == DeviceStatus.UNDER_MAINTENANCE])

        high_risk_devices = len([d for d in self.devices if d.risk_level >= 5])
        low_risk_devices = len([d for d in self.devices if d.risk_level < 5])

        return (f"Total Devices: {total_devices}\n"
                f"Active Devices: {active_devices}\n"
                f"Inactive Devices: {inactive_devices}\n"
                f"Under Maintenance: {maintenance_devices}\n"
                f"High Risk Devices (Risk Level >= 5): {high_risk_devices}\n"
                f"Low Risk Devices (Risk Level < 5): {low_risk_devices}\n")


# Define the RBAC system
class AccessControl:
    def __init__(self):
        self.users: Dict[str, User] = {}

    def add_user(self, username: str, role: Role, is_active: bool = True):
        self.users[username] = User(username, role, is_active)

    def check_access(self, user: User, action: str) -> bool:
        """Check if the user has permission to perform the action."""
        if not user.is_active:
            print(f"Access Denied: User {user.username} is inactive.")
            return False
       
        if action == "view_report":
            return user.role in [Role.VIEWER, Role.MANAGER, Role.ADMIN]
        elif action == "modify_report":
            return user.role in [Role.MANAGER, Role.ADMIN]
        elif action == "add_device":
            return user.role == Role.ADMIN
        elif action == "approve_recommendation":
            return user.role == Role.MANAGER
        return False


# Example usage
if __name__ == "__main__":
    # Create users with different roles interactively
    access_control = AccessControl()
    num_users = int(input("How many users do you want to create? "))
    for _ in range(num_users):
        username = input("Enter username: ")
        role = input("Enter role (viewer, manager, admin): ").lower()
        role = Role[role.upper()] if role in Role.__members__ else Role.VIEWER
        access_control.add_user(username, role)

    # Create and manage the device report
    report = DeviceReport()

    # Allow manager or admin to add devices
    while True:
        device_action = input("\nWould you like to add a new device? (yes/no): ").lower()
        if device_action == "no":
            break
        elif device_action == "yes":
            device_id = input("Enter device ID: ")
            device_type = input("Enter device type (smart_light, thermostat, security_camera, door_lock): ").lower()
            firmware_version = input(f"Enter firmware version for {device_type}: ")
            device_status = input("Enter device status (active, inactive, under maintenance): ").lower()
            status = DeviceStatus[device_status.upper()] if device_status in DeviceStatus.__members__ else DeviceStatus.ACTIVE
            new_device = IoTDevice(device_id=device_id, device_type=device_type, firmware_version=firmware_version, status=status)
            report.add_device(new_device)
            print(f"Device {new_device.device_id} added.")

    # If the user is a manager/admin, allow them to add recommendations
    user_type = input("\nEnter user type (viewer, manager, admin): ").lower()
    username = input("Enter username: ")
    user = access_control.users.get(username)

    if access_control.check_access(user, "view_report"):
        print("\nDevice Report:")
        print(report.generate_report())
        print("Recommendations:")
        print(report.view_recommendations())

        # If Manager/Admin, allow adding recommendations
        if user.role in [Role.MANAGER, Role.ADMIN]:
            while True:
                recommendation_action = input("\nWould you like to add a recommendation? (yes/no): ").lower()
                if recommendation_action == "no":
                    break
                elif recommendation_action == "yes":
                    recommendation_text = input("Enter recommendation description: ")
                    new_recommendation = Recommendation(description=recommendation_text)
                    report.add_recommendation(new_recommendation)
                    print(f"Recommendation added: {new_recommendation}")

            # Allow managers to approve recommendations
            while True:
                approval_action = input("\nWould you like to approve a recommendation? (yes/no): ").lower()
                if approval_action == "no":
                    break
                elif approval_action == "yes":
                    print("\nPending Recommendations:")
                    print(report.view_recommendations())
                    index = int(input("Enter the recommendation number to approve: ")) - 1
                    if 0 <= index < len(report.recommendations):
                        report.recommendations[index].approve()
                        print("Recommendation approved.")
                    else:
                        print("Invalid recommendation index.")
           
    # View advanced statistics
    statistics_action = input("\nDo you want to view the statistics? (yes/no): ").lower()
    if statistics_action == "yes":
        print("\nAdvanced Statistics:")
        print(report.generate_statistics())