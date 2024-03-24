import numpy as np

def get_bearing(AX,AY,BX,BY):
    # returns the clockwise angle between the Y axis and the line AB
    AB = np.sqrt(((AX-BX)**2) + ((AY-BY)**2))
    if AY == BY:
        if AX == BX:
            print ('**** ERROR. A and B are in the same location')
            return False
        elif AX > BX:
            NAB = np.radians(270.0)
        else:
            NAB = np.radians(90.0)
    elif AX == BX:
        if AY > BY:
            NAB = np.radians(180.0)
        else:
            NAB = np.radians(0.0)
    elif AX > BX:
        if AY > BY:
            NAB = np.radians(180.0) + np.arcsin((AX-BX)/(AB))
        else:
            NAB = np.radians(360.0) - np.arcsin((AX-BX)/(AB))
    else:
        if AY > BY:
            NAB = np.radians(180.0) - np.arcsin((BX-AX)/(AB))
        else:
            NAB = np.arcsin((BX-AX)/(AB))
    return NAB

# triangle with sides A,B,C going clockwise
# angle alpha is opposite side A, beta opposite B, gamma opposite C
# angles are in radians

def get_triangle_1(A, beta, gamma): # returns triangle knowing one side and the two angles at each end
                                    # in order going clockwise
    alpha = np.pi - (beta + gamma)
    # difference from V02 is abs
    B = A * np.sin(beta) / np.sin(alpha)
    C = A * np.sin(gamma) / np.sin(alpha)
    return A,B,C,alpha,beta,gamma  

def get_triangle_2_a(A, B, alpha):
    # returns triangle knowing two sides and the angle opposite the first side
    beta = np.arcsin(B * np.sin(alpha) / A)
    gamma = np.pi - (beta + alpha)
    C = A * np.sin(gamma) / np.sin(alpha)
    return A,B,C,alpha,beta,gamma

def get_triangle_2_b(A,B,gamma):
    # returns triangle knowing two sides and the included angle
    C = np.sqrt(A**2 + B**2 - (2 * A * B * np.cos(gamma)))
    A,B,C,alpha,beta,gamma = get_triangle_3(A,B,C)
    return A,B,C,alpha,beta,gamma

def get_triangle_3(A,B,C): # returns triangle knowing three sides
    cosgamma = ((A**2)+(B**2)-(C**2))/(2*A*B)
    #print ('cosgamma',cosgamma)
    gamma = np.arccos(cosgamma)
    cosbeta = ((A**2)+(C**2)-(B**2))/(2*A*C)
    #print ('cosbeta',cosbeta)
    beta =  np.arccos(cosbeta)
    alpha = np.pi - (gamma + beta)
    return A,B,C,alpha,beta,gamma

def print_triangle(triangle_result, labels_supplied=False):
    A,B,C,alpha,beta,gamma = triangle_result
    if not labels_supplied:
        AL,BL,CL,alphaL,betaL,gammaL = ('A','B','C','alpha','beta','gamma')
    else:
        AL,BL,CL,alphaL,betaL,gammaL = labels_supplied
    print (AL,'{:7.2f}, '.format(A),
           BL,'{:7.2f}, '.format(B),
           CL,'{:7.2f}, '.format(C),
           alphaL,'{:7.2f}, '.format(np.degrees(alpha)),
           betaL,'{:7.2f}, '.format(np.degrees(beta)),
           gammaL,'{:7.2f}'.format(np.degrees(gamma)))

def get_coordinates(distance,angle):    #  angle is clockwise from y axis (= 'North')
    xdelta = distance * np.sin(angle)
    ydelta = distance * np.cos(angle)
    return xdelta, ydelta

def print_coordinates(distance, angle, x, y):
    print ('distance {:7.2f}'.format(distance),
           ' angle {:7.2f}'.format(angle),
           ' x {:7.2f}'.format(x),
           ' y {:7.2f}'.format(y))
   
def get_distance(lx, ly, rx, ry):
    #  calculates distance between l(x,y) and r(x,y)
    d = np.sqrt((lx-rx)**2 + (ly-ry)**2)
    return d
