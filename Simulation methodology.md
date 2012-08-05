# Simulation Methodology

In the simulation, players are assigned one resource and an arbitrary number of objectives. A *resource* is unique to each player and essentially represents that player's competitive advantage, or supply in the market. Players have a set number of differently valued *objectives,* which correspond to market demand. Resources are represented with uppercase Latin letters (i.e. `A`, `B`, `C`) and objectives with lowercase Latin letters and numerals (i.e. `a1`, `a2`, `b1`, `c2`). Objectives with a subscripted 1 (i.e. `a1`) are classified as high-value, while objectives with a subscripted 2 are classified as low-value. Objective values can be arbitrarily set in the simulation, but by default high-value objectives are worth 20 points, while low-value objectives are worth 10.

Objectives only benefit players when they match a player's assigned resource. For example, a player assigned resource `A` and objectives `a1`, `a2`, `b2`, `c1`, and `c2` would have 30 points, as `a1` (20 points) and `a2` (10 points) match the player's resource. The remaining three objectives (`b2`, `c1`, and `c2`) represent unmet demand and provide the incentive for that player to network with other players with different resources (specifically `B` and `C`). 

Players are assigned resources and objectives at the outset of the simulation. The simulation builds a pool of resources distributed in frequency according to a given ratio. For example, Table X demonstrates the resource pool in a simulation with 16 players, 4 different types of objectives, and an approximate ratio of 3:1. 

Resource | Quantity  
-------- | ------  
`A`      | 6  
`B`      | 6  
`C`      | 2  
`D`      | 2  

After building a pool of resources, the simulation then creates a larger pool of objectives of varying value, again distributed in frequency according to a given ratio. Table X shows the objective pool for the sample 16-person, 4-resource example above, assuming there are 5 objectives per player distributed at an approximate ratio of 3:1.

Objective | Quantity | Frequency | Value  
--------- | -------- | --------- | ---  
`a1`      | 15       | High      | High  
`a2`      | 15       | High      | Low  
`b1`      | 5        | Low       | High  
`b2`      | 5        | Low       | Low  
`c1`      | 5        | Low       | High  
`c2`      | 5        | Low       | Low  
`d1`      | 15       | High      | High  
`d2`      | 15       | High      | Low  


Each player is then randomly assigned one resource and a given number of objectives. In the ongoing example with 16 players, final resource and objective assignments are shown in Table X. 

Player    | Resource | Objectives                   | Value  
--------- | -------- | ---------------------------- | ---  
Player 00 | `C`      | `a2`, `d2`, `b2`, `c2`, `d2` | 10  
Player 01 | `B`      | `d1`, `d2`, `d2`, `a1`, `a2` | 0  
Player 02 | `D`      | `d2`, `d2`, `d2`, `d1`, `a1` | 50  
Player 03 | `B`      | `d1`, `d1`, `a1`, `d1`, `c1` | 0  
Player 04 | `A`      | `a1`, `d2`, `a1`, `d1`, `c2` | 40  
Player 05 | `D`      | `a1`, `c1`, `a2`, `d1`, `b2` | 20  
Player 06 | `C`      | `b1`, `d1`, `a2`, `d1`, `d2` | 0  
Player 07 | `B`      | `c2`, `d1`, `c2`, `b1`, `d2` | 20  
Player 08 | `B`      | `a2`, `a2`, `a2`, `a1`, `d1` | 0  
Player 09 | `A`      | `a1`, `d2`, `a1`, `a2`, `a2` | 60  
Player 10 | `B`      | `a2`, `d2`, `a1`, `a1`, `d1` | 0  
Player 11 | `B`      | `b1`, `a1`, `d1`, `a1`, `b1` | 40  
Player 12 | `A`      | `a2`, `d1`, `b2`, `a2`, `c1` | 20  
Player 13 | `A`      | `c2`, `a2`, `a1`, `d2`, `a1` | 50  
Player 14 | `A`      | `d1`, `c1`, `a2`, `b2`, `b1` | 10  
Player 15 | `A`      | `a2`, `c1`, `b2`, `d2`, `d2` | 10  

Once the resource and objective pools have been assigned, players randomly interact with each other and create networks in order to fulfill the unmet resource their objectives demand. Players are aware of the resources others have to offer, but not the objectives of others. Networking decisions are made according to a logical algorithm based on the number of points a player would gain by creating a network. 

In the ongoing example, Player 5 has resource `D` and a total of 20 points, with only one objective `d1` matching their resource. When Player 5 meets Player 10, who has `B` and no objectives that match, Player 5 would gain 10 points by creating a network with Player 10—Player 10's `B` would fulfill the unmet `b2`. Player 10 would also benefit from a network—having access to Player 5's `D` would give Player 10's `d1` and `d2` and net 30 additional points. Because the network would be mutually beneficial, the two players create a network and pool their resources together. Future players can then enter that network and add their resources to the shared pool. 

When two players meet, one player is given precedence in decision-making, and each player acts in their own self-interest.  A player can only be in one network at a time. When deciding to network, the requesting player can either (1) choose to stay in their existing network and request that the responding player join, or (2) attempt to leave their existing network and request to join the network of the responding player. A network or exchange will only be created when both players benefit to some degree.

For example, if Player 5 were to gain no benefit from collaboration with Player 10, but Player 10 could potentially gain points from leaving their current network and joining that of Player 5, Player 5 would refuse to network because there would be no benefit to them personally. Likewise, if Player 5 were to gain points from having Player 10 join their team, Player 10 would refuse if there were a lack of personal benefit.  In instances where the requesting player would gain equal benefit from leaving their existing network or joining the responding player's network, the player chooses to stay or leave at random. 

There are four variations in the networking algorithm. In its simplest form, both interacting players must agree to network. In the second variation, each player has a limit of one network partner. In the third variation, the requesting player must drop one objective of their choice and leave it unfulfilled. In the fourth variation, a player must offer one objective of their choice as payment, and the responding player must accept the offer.