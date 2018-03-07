import numpy as np

import rl_agent as rl

import pdb


env = rl.envs.Gridworld(4, 4, random_start=True)
env.set_state(0, 3, 'terminal')
env.set_state(3, 0, 'terminal')


agent = rl.AgentSARSA(
    state_space=env.observation_space,
    action_space=env.action_space,
    discount=1.0,
    start_learning_at=0,
    q_fun_approx=rl.TabularApproximator(
        step_size=0.02,
        init_val=0),
    policy=rl.QMaxPolicy(
        expl_start=False,
        nb_rand_steps=0,
        e_rand_start=0.1,
        e_rand_target=0.001,
        e_rand_decay=0.001
        )
    )


done = True
while True:

    if done:
        obs, rew, done = env.reset(), None, False
    else:
        obs, rew, done = env.step(act)

    env.render()
    print('obs:', obs)
    print('rew:', rew)
    print('done:', done)

    

    agent.observe(obs, rew, done)

    #pdb.set_trace()
    agent.learn()

    print('Q_max:')
    print(np.sum(agent.Q._weights, axis=1).reshape([4, 4]) / 4)

    act = agent.take_action(obs)
    # print('pick action (0=N, 1=E, 2=S, 3=W)')
    # act = int(input())



    agent.next_step(done)



    


    print('===========')






