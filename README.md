# SAND
> Juan desde México llega a la frontera de Estados Unidos con su bicicleta.
> Él tiene dos bolsas grandes sobre sus hombros.
> El guardia lo detiene y le dice: "¿Qué hay en las bolsas?"
> "Arena", responde Juan.
> El guardia dice: "Ya veremos, ¡baje de la bicicleta!"
> El guardia toma las bolsas y las rompe, las vacía y no encuentra nada en ellas excepto arena.
> Él detiene a Juan durante la noche y analiza la arena, solo para descubrir que no hay nada más que arena pura en las bolsas.
> ...

The story of a smugler [link](https://steemit.com/spanish/@nkdksk/juan-desde-mexico-llega-a-la-frontera-de-estados-unidos-con-su-bicicleta)

## What is it?
This small application uses network speed to smugle information from a machine to another.

## How does it work?
Dummy packets are sent from the client to the server limiting the speed to form 0s and 1s, the server takes this packet speeds and forms the file that the client tried to send.

## Limitations and future works
- We use python's time library to wait between packets, this limits our speed as the sleep function has a minimum sleeping time value. 
- In order to make this tool "undetectable" the dummy packets must mimic a commonly used protocol. Currently we just send pokemon pictures but this should be changed.
- Some thresholds and values need to be fine tuned in order to make this tool work in larger networks.
