def main():
    import pygame
    from random import randint as r

    NUMBODIES = 50
    COEFFICIENT = 1
    MAXSPEED = 5
    MINSPEED = -5
    MAXMASS = 20
    MINMASS = 10
    MAXSIZE = 20
    MINSIZE = 1
    BODIES = []

    class body():
        def __init__(self, velocity:list, position:list, mass:float, scale:float) -> None:
            self.velocity = pygame.Vector2(velocity)
            self.position = pygame.Vector2(position)
            self.mass = mass
            self.scale = scale

        def setVelocity(self,speed:list) -> None:
            self.velocity = pygame.Vector2(speed)
        
        def getVelocity(self) -> pygame.Vector2:
            return self.velocity
        
        def setPosition(self,position:list) -> None:
            self.position = pygame.Vector2(position)
        
        def getPosition(self) -> pygame.Vector2:
            return self.position
        
        def setMass(self, mass:float) -> None:
            self.mass = mass

        def getMass(self) -> float:
            return self.mass
        
        def setScale(self, scale:float) -> None:
            self.scale = scale

        def getScale(self) -> float:
            return self.scale

    def sim_active() -> bool:
        return not pygame.QUIT in [event.type for event in pygame.event.get()]
 
    def update_screen() -> None:
        pygame.display.update()
    
    def clear_screen(screen:pygame.surface) -> None:
        screen.fill([0,0,0])

    def draw_body(screen:pygame.surface, body:body) -> None:
        pygame.draw.circle(screen, [body.getMass()*10,body.getMass()*10,body.getMass()*10], body.getPosition(), body.getScale())

    def check_body_collision(body1:body,body2:body) -> bool:

        vector_distance = (body1.getPosition() - body2.getPosition()).magnitude_squared()

        if 0 < vector_distance < (body1.getScale() + body2.getScale())**2:
            return True
        else:
            return False 

    def check_wall_collision(body:body, screen_size:list) -> bool:
        posx,posy = body.getPosition()
        size = body.getScale()

        if posx+size > screen_size[0] or posx-size < 0:
            return True, "X"

        elif posy+size > screen_size[1] or posy-size < 0:
            return True, "Y"

        else:
            return False, None

    def collide_body(body1:body, body2:body) -> None:

        mass1 = body1.getMass()
        mass2 = body2.getMass()

        position1 = body1.getPosition()
        position2 = body2.getPosition()

        velocity1 = body1.getVelocity()
        velocity2 = body2.getVelocity()

        distsqared1 = max(((position1-position2).magnitude_squared(),1))
        distsqared2 = max(((position2-position1).magnitude_squared(),1))

        massScalar1 = 2*mass2/(mass1+mass2)
        massScalar2 = 2*mass1/(mass2+mass1)

        collisionNormal1 = position1-position2
        collisionNormal2 = position2-position1

        velocityProjection1 = (velocity1-velocity2).dot(collisionNormal1)
        velocityProjection2 = (velocity2-velocity1).dot(collisionNormal2)

        normalizedVelocity1 = massScalar1*velocityProjection1/distsqared1 * (collisionNormal1)
        normalizedVelocity2 = massScalar2*velocityProjection2/distsqared2 * (collisionNormal2)

        newVelocity1 = (velocity1 - normalizedVelocity1) * COEFFICIENT
        newVelocity2 = (velocity2 - normalizedVelocity2) * COEFFICIENT

        body1.setVelocity(list(newVelocity1))
        body2.setVelocity(list(newVelocity2))
       
    def collide_wall(body1:body, wall:str) -> None:
        velx,vely = body1.getVelocity()

        if wall == "X":
            newvel = pygame.Vector2([-velx,vely]) * COEFFICIENT
            body1.setVelocity(list(newvel))

        elif wall == "Y":
            newvel = pygame.Vector2([velx,-vely]) * COEFFICIENT
            body1.setVelocity(list(newvel))

    def find_prev_body() -> body:
        return BODIES[-2].getPosition() if len(BODIES) > 1 else [MAXSIZE, MAXSIZE*2]

    def space_bodies(screen_size:pygame.surface, newBody:body) -> None:

        size = newBody.getScale()
        offset = 2*size + MAXSIZE + 10

        lastX,lastY = find_prev_body()

        if lastX + 2*offset > screen_size[0]:
            lastX = 0
            lastY = lastY + 2*offset 

        if lastY + offset > screen_size[1]:
            print("Too many bodies. Deleting extra bodies")
            del BODIES[-1]

        newpos = [lastX + offset, lastY]

        newBody.setPosition(newpos)

    def populate_bodies(screen:pygame.surface, screen_size:list) -> None:

        for _ in range(NUMBODIES):
            
            speed = [r(MINSPEED,MAXSPEED),r(MINSPEED,MAXSPEED)]
            position = [0,0]   
            mass = r(MINMASS,MAXMASS)
            scale = r(MINSIZE,MAXSIZE)
            
            newBody = body(speed,position,mass,scale)
                    
            BODIES.append(newBody)

            space_bodies(screen_size,newBody)

            draw_body(screen,newBody)
    
    def unstick_bodies(body1:body, body2:body) -> None:        

        collision_dir = body1.getPosition() - body2.getPosition()

        while check_body_collision(body1, body2):
            body1.setPosition(body1.getPosition() + collision_dir * 0.01)

    def unstick_wall(body1:body) -> None:
        posx,posy = body1.getPosition()
        size = body1.getScale()
        offset = size

        if posx+size > screen_size[0]:
            body1.setPosition([screen_size[0]-offset,posy])
        if posx-size < 0:
            body1.setPosition([offset,posy])
        if posy+size > screen_size[1]:
            body1.setPosition([posx,screen_size[1]-offset])
        if posy-size < 0:
            body1.setPosition([posx,offset])

    def update_bodies(screen:pygame.surface, millis:int) -> None:
        for Body in BODIES:
            Body.setPosition(list(Body.getPosition() + Body.getVelocity()*millis*0.01))
            draw_body(screen,Body)

    pygame.init()
    screen_surface = pygame.display.set_mode((0,0))
    clock = pygame.time.Clock()
    screen_size = pygame.display.get_window_size()

    populate_bodies(screen_surface, screen_size)

    while sim_active():

        millis = clock.tick_busy_loop(360)

        for currentBODY in BODIES:
            for newBODY in BODIES:
                if newBODY is not currentBODY:
                    if check_body_collision(currentBODY,newBODY):
                        unstick_bodies(currentBODY,newBODY)
                        collide_body(currentBODY,newBODY)
            
            collision, wall = check_wall_collision(currentBODY, screen_size)
            if collision:
                unstick_wall(currentBODY)
                collide_wall(currentBODY,wall)
        
            currentBODY.setVelocity(list(currentBODY.getVelocity() - pygame.Vector2([0,-0.98])))
        
        clear_screen(screen_surface)
        update_bodies(screen_surface, millis)
        update_screen()

if __name__ == "__main__":
    main()