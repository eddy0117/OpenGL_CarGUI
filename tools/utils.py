import numpy as np

def twoD_2_threeD(x_2d, y_2d, z, intrinsic):  # input is a 2D point and depth value
    '''
    Given 2D points, a depth value, and an intrinsic camera matrix,
    outputs the 3D point coordinates.
    '''
    # Create a 3D point in homogeneous coordinates
    x_y_z = np.array([x_2d * z, y_2d * z, z])

    # Compute the inverse of the intrinsic matrix
    intrinsic_inv = np.linalg.inv(intrinsic)

    # Transform the 2D point back into 3D space
    x_y_z_3d = np.dot(intrinsic_inv, x_y_z)

    # Extract the 3D coordinates
    x_3d, y_3d, z_3d = x_y_z_3d

    return x_3d, y_3d, z_3d

def rotate_2d_point(x, y, ang):
    theta = np.radians(ang)
    # Define the rotation matrix
    rotation_matrix = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    # Original point as a column vector
    point = np.array([x, y])

    # Apply the rotation matrix to the point
    rotated_point = np.dot(rotation_matrix, point)

    # Extract the rotated coordinates
    x_rotated, y_rotated = rotated_point

    return x_rotated, y_rotated