import numpy as np
import matplotlib.pyplot as plt
from celluloid import Camera
from tqdm import tqdm

plt.style.use('dark_background')

import argparse

parser = argparse.ArgumentParser(description='Exoplanet Transit Script')



parser.add_argument('-num_frames', type=int,
                    help="""This number tells the script how many frames you want in your animation. Default is 200.""")

parser.add_argument('-planet_radius', type=float,
                    help="""The radius of your planet. Default value is 0.3""")

parser.add_argument('-star_radius', type=float, 
                    help="""The radius of your star. Default value is 5.0""")

parser.add_argument('-camera_distance', type=float, 
                    help="""The distance the camera is away from the system. Default value is 8.0""")

parser.add_argument('-dark_mode', type=bool, 
                    help="""The default background mode of the animation. Default value is True""")

   

results = parser.parse_args()


if results.num_frames:
    print("Number of Frames is {0}".format(results.num_frames))
else:
    results.num_frames=200
    print("Number of Frames is {0}".format(results.num_frames))
    
if results.planet_radius:
    print('Planet Radius = {0}'.format(results.planet_radius))
else:
    results.planet_radius=0.3
    print('Planet Radius = {0}'.format(results.planet_radius))
    
if results.star_radius:
    print('Star Radius = {0}'.format(results.star_radius))
else:
    results.star_radius=5.0
    print('Star Radius = {0}'.format(results.star_radius))
    
if results.camera_distance:
    print('Camera Distance = {0}'.format(results.camera_distance))
else:
    results.camera_distance=8.0
    print('Camera Distance = {0}'.format(results.camera_distance))
    
if results.dark_mode:
    print('Dark Mode = {0}'.format(results.dark_mode))
else:
    results.dark_mode=True
    print('Dark Mode = {0}'.format(results.dark_mode))
    

class Body:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius
        self.angular_size = 1

    def calc_position(self, t):
        """
        A function to update the position of the planet. We use a simple parametric 
        equation in cylindrical coordinates.
        """
        x,y,z = 2*np.cos(((t * 2* np.pi) / (N_frames))+ np.pi/2), 2*np.sin(((t * 2* np.pi) / (N_frames)) + np.pi/2), 0
        self.position = np.array([x, y, 0 ])
        
    def calc_projection(self, t):
        """
        We set up a camera in the y-plane to compute the projected perspective.
        """
        camera_ = np.array([0,-1 * Camera_Distance, 0])
        dr_vec = self.position - camera_
        distance = np.linalg.norm(dr_vec)
        
        self.angular_size = self.radius / distance
        
        return distance

def area_overlap(circle_A, circle_B):
    """
    A function to compute the overlapping projected area of 2 circles (using angular size for perspective).
    """
    
    d = np.sqrt((circle_B.position[0] - circle_A.position[0])**2 + (circle_B.position[2] - circle_A.position[2])**2)

    if d < (circle_A.angular_size + circle_B.angular_size):
        
        a = circle_A.angular_size**2
        b = circle_B.angular_size**2
        
        x = (a - b + d**2) / (2 * d)
        z = x**2

        y = np.sqrt(np.abs(a - z))

        if d <= np.abs(circle_B.angular_size - circle_A.angular_size):
            AREA = np.pi * min(a, b)
        else:  
            AREA = a * np.arcsin(y / circle_A.angular_size) + b * np.arcsin(y / circle_B.angular_size) - y * (x + np.sqrt(z + b - a))
        
        return AREA
    
    return 0
    
    
def calc_blocked_light(star,planet, t):
    """
    A function to calculate the amount of light blocked by the planet.
    """
    area_star = np.pi * star.angular_size**2
    
    d_planet = planet.calc_projection(t)
    d_sun = star.calc_projection(t)
    
    if d_planet < d_sun:
        area_planet = area_overlap(star,planet)
    else:
        area_planet = 0
        

    return 1 - (area_planet / area_star)


def draw(axes, camera, t, Sun, Planet, brightness_curve, times):
    """
    A function to draw the exoplanet orbit and the lightcurve.
    """
    
    #physics
    Planet.calc_position(t)
    
    d_planet = Planet.calc_projection(t)
    d_sun = Sun.calc_projection(t)
    
    brightness_dip = calc_blocked_light(Sun,Planet, t)
    brightness_curve.append(brightness_dip)
    times.append(t)
    
    #plotting
    if Dark_Mode:
        lightcurve_color="white"
        planet_color="cyan"
    else:
        lightcurve_color="black"
        planet_color="blue"
     
    star_color="red"
        
    axes[1].plot(times, brightness_curve, color=lightcurve_color)
    axes[1].plot(times[-1], brightness_curve[-1], marker="o", color=lightcurve_color)
    
    axes[1].set_ylim(0.99,1.002)
    axes[1].set_xlim(0,N_frames)
    axes[1].set_xlabel("Days")
    axes[1].set_ylabel("Brightness Dip")
    
    if d_planet > d_sun:
        
        planet = plt.Circle((Planet.position[0], Planet.position[2]), Planet.angular_size, color=planet_color)
        axes[0].add_patch(planet)
        
        sun = plt.Circle((Sun.position[0],Sun.position[1]), Sun.angular_size, color=star_color, zorder=10)
        axes[0].add_patch(sun)
        
    else:
        sun = plt.Circle((Sun.position[0],Sun.position[1]), Sun.angular_size, color=star_color)
        axes[0].add_patch(sun)
        
        planet = plt.Circle((Planet.position[0], Planet.position[2]), Planet.angular_size, color=planet_color, zorder=10)
        axes[0].add_patch(planet)
        
    plt.tight_layout()
        
    camera.snap()
    
def main():
    """
    Main loop hosted within this function. This runs the entire simulation.
    """

    #setup the sim
    Sun = Body(np.zeros(3), Star_Radius)
    Planet = Body(np.array([0,1,0]), Planet_Radius)
    
    #create the figure
    fig, axes = plt.subplots(2,1, figsize=(6, 6), gridspec_kw={'hspace':0.0})
    axes[0].set_title("Exoplanet Transit", pad = 10)
    axes[0].set_xticks([]); axes[0].set_yticks([])
    axes[0].set_xlim(-3,3), axes[0].set_ylim(-3,3)
    axes[0].axis('equal')

    
    camera = Camera(fig)

    brightness_curve, times = [], []
    #Main Loop for Simulation!
    for frame in tqdm(range(N_frames)):
        draw(axes, camera, frame, Sun, Planet, brightness_curve, times)
        
    animation = camera.animate(blit=True)

    #save animation
    animation.save('outputs/exoplanet.gif', fps=30)
    

if __name__ == "__main__":
    N_frames = results.num_frames
    Star_Radius = results.star_radius
    Planet_Radius = results.planet_radius
    Camera_Distance = results.camera_distance
    Dark_Mode = results.dark_mode
    main()