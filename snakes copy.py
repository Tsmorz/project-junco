import os
import glob
import time
from datetime import datetime

import matplotlib.pyplot as plt

import numpy as np
from numpy import matlib

import gym
import pygame

import random
import sys


import time


class Drone():
    m = 3.2
    Iyy = 1/12*m*0.8**2

    S = 0.25
    c = 0.13

    Cl_0 = 0.5
    Cl_alpha = 0.17
    
    Cd_0 = 0.02
    K = 0.01

    Cm_0 = -0.05
    Cm_alpha = 0.2
    Cm_alpha_dot = -0.1
    Cm_delta_e = 0.5

    def __init__(self):
        self.x_thres = 1000
        self.z_thres = 100
        self.v_thres = 50
        self.theta_thres = np.pi/6
        self.theta_dot_thres = np.pi
        self.gamma_thres = np.pi/6

        self.limits = np.array([
            self.x_thres,
            self.z_thres,
            self.v_thres,
            self.theta_thres,
            self.theta_dot_thres,
            self.gamma_thres
        ])

        self.state = None
        self.prev_action = None
        self.steps_beyond_terminated = None

        self.time = 0.
        self.dt = 0.05

    def lift(self,rho):
        vel = self.state[2]
        alpha = self.state[3] - self.state[4]

        Cl = self.Cl_0 + self.Cl_alpha*alpha

        return 0.5*rho*vel**2*self.S*Cl
    
    def drag(self,rho):
        vel = self.state[2]
        alpha = self.state[3] - self.state[4]

        Cl = self.Cl_0 + self.Cl_alpha*alpha
        Cd = self.Cd_0 + self.K*Cl**2

        return 0.5*rho*vel**2*self.S*Cd
    
    def moment(self,alpha_dot,delta_e,rho):
        vel = self.state[2]
        alpha = self.state[3] - self.state[4]
        Cm = self.Cm_0 + self.Cm_alpha*alpha + self.Cm_alpha_dot*alpha_dot + self.Cm_delta_e*delta_e

        return 0.5*rho*vel**2*self.S*self.c*Cm
    
    def step(self, action):
        err_msg = f"{action!r} ({type(action)}) invalid"
        assert self.state is not None, "Call reset before using step method."
        
        g = 9.81
        m = self.m
        self.time += self.dt
        rho = np.random.normal(1.225,0.01)

        L = self.lift(rho)

        # if L <= m*g and self.state[1]<=0.1:
        #     x, z, v, theta, theta_dot, gamma = np.array([self.state[0],0,self.state[2],0,0,0])
        # else:
        #     x, z, v, theta, theta_dot, gamma = self.state
        x, z, v, theta, theta_dot, gamma = self.state
        thrust, delta_e = action

        D = self.drag(rho)

        alpha = theta - gamma
        v_dot = (-D - m*g*np.sin(gamma) + thrust*np.cos(alpha)) / m
        gamma_dot = -(-L + m*g*np.cos(gamma) + thrust*np.sin(alpha)) / (m*v)
        x_dot = v*np.cos(gamma)
        z_dot = -v*np.sin(gamma)

        alpha_dot = theta_dot - gamma_dot
        M = self.moment(alpha_dot,delta_e,rho)
        theta_ddot = M / self.Iyy


        # integrate
        x += x_dot*self.dt
        z += z_dot*self.dt
        v += v_dot*self.dt
        theta += theta_dot*self.dt + theta_ddot*self.dt**2
        theta_dot += theta_ddot * self.dt
        gamma += gamma_dot*self.dt

        state = np.array([x,z,v,theta,theta_dot,gamma])
        action = np.array([thrust,delta_e])

        self.state = (list(np.reshape(state,(6,))))

        terminated = bool(
            x < -self.x_thres
            or x > self.x_thres
            or z < -self.z_thres
            or z > self.z_thres
            or v < -self.v_thres
            or v > self.v_thres
            or theta < -self.theta_thres
            or theta > self.theta_thres
            or theta_dot < -self.theta_dot_thres
            or theta_dot > self.theta_dot_thres
            or gamma < -self.gamma_thres
            or gamma > self.gamma_thres
        )

        if not terminated:
            reward = 1.0
        elif self.steps_beyond_terminated is None:
            self.steps_beyond_terminated = 0
            reward = 0.0
        else:
            if self.steps_beyond_terminated == 0:
                gym.logger.warn(
                    "You are calling 'step()' even though this "
                    "environment has already returned terminated = True. You "
                    "should always call 'reset()' once you receive 'terminated = "
                    "True' -- any further steps are undefined behavior."
                )
            self.steps_beyond_terminated += 1
            reward = 0.0

        return state, reward, terminated, False

    def reset(self):
        self.state = np.array([0,0,15,0,0,0])
        self.steps_beyond_terminated = None
        self.time = 0

        return self.state

    def close(self):
        pass


pygame.init()
env = Drone()
state = env.reset()
action = np.array([100,0])

fig, ax = plt.subplots(1,figsize=(10,5))
traj = []

last_presses = None
t = 0
while t<1000:
    state, reward, done, _ = env.step(action)
    x = state[0]
    z = -state[1]
    v = state[2]
    theta = -state[3]
    theta_dot = -state[4]
    gamma = state[5]
    traj.append((x,z))

    action = np.array([0,0])
        
    if v<25:
        action[0] = 100
    else:
        action[0] = 0
    action[1] = 0.965

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            print(event.key)
            if event.key == pygame.K_UP:
                action[1] = 1
            elif event.key == pygame.K_DOWN:
                action[1] = -1
        else:
            action[1] = 0

        
    l = 0.8
    plt.plot([x,x+0.25*l*np.cos(theta)],[z,z+0.25*l*np.sin(theta)],'k-')
    plt.plot([x,x-0.75*l*np.cos(theta)],[z,z-0.75*l*np.sin(theta)],'k-')
    plt.xlim(x-20,x+80)
    plt.ylim(z-25,z+25)

    beam = 50
    angle = 60*np.pi/180
    plt.plot([x,x+beam*np.cos(theta+angle/2)],[z,z+beam*np.sin(theta+angle/2)],'k--')
    plt.plot([x,x+beam*np.cos(theta-angle/2)],[z,z+beam*np.sin(theta-angle/2)],'k--')
    xs = x+beam*np.cos(theta+np.linspace(-angle/2,angle/2,10))
    zs = z+beam*np.sin(theta+np.linspace(-angle/2,angle/2,10))
    plt.plot(xs,zs,'k.',markersize=1)

    x,z = zip(*traj)
    plt.plot(x,z,'b-',markersize=1)

    plt.show()
    plt.pause(0.01)
    t+=1

    if done:
        break
    else:
        ax.clear()
                
print(np.around(state,2), reward, done)
env.close()