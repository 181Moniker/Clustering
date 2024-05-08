#Author: Jonathan Ridley
#Last Edited: 5/8/2024 - 9:20pm
import pygame, sys
import random as r
import time
import math as m

#Will be used to randomly generate coordinated according to the bounds of the pygame window
def generate_pos(wdth, hgth) -> tuple: #return tuple
    x = r.randrange(0, wdth, 25)
    y = r.randrange(0, hgth, 20)
    return (x,y) #return randomly generated position

coords_list = []
#This will be used to find the new mean for K (K serves as a cluster center)
def find_mean(clst) -> float: #return float
    global variance_list, coords_list
    new_clst = {}
    var_list = []
    for key, value in clst.items():
        sum_x, sum_y = 0, 0 #will be used to find the sum of all x and y coords, respectively
        try:
            dist_groups = []#create list for a grouping's euclidean distances
            coords_list = []#create list for groups of data points per mean
            for i in range(len(value)):
                dist_groups.append(value[i][1]) #adds the euclidean distance to list
                sum_x += value[i][0][0] #add onto the sum of x coords
                sum_y += value[i][0][1] #add onto the sum of y coords
                coords_list.append(value[i][0]) #coords_list_mini.append(value[i][0])
            var_list.append(dist_groups) #adds grouping of euclidean distances to another list
            sum_x /= len(value); sum_x = round(sum_x, 2) #find and round the mean of the sum of Xs
            sum_y /= len(value); sum_y = round(sum_y, 2) #find and round the mean of the sum of Ys
            print(f"{key} for {value} | {(sum_x, sum_y)}")
            new_clst[(sum_x,sum_y)] = coords_list #list(set(coords_list)) #add the new coords to the dict
        except ZeroDivisionError: pass
    variance_list = var_list #variance list adopts each groupings' euclidean distances
    return new_clst #send the new dict, which is full of new coords based on the means of the data points per cluster center, off


#receives a list of euclidean distances, gets the index of the lowest dist of the list, takes the lowest element,
#and adds it to the list of the key with the same index
def find_min(dct, clst, last_el=False) -> dict: #return dict
    dct_lst = list(dct.values())[0] #make a list out of the dictionary's 'dct's values
    min = dct_lst[0] #set lowest value to first element in list
    go_to = 0 #variables serves as the index of lowest number to be found in the above list
    for i in range(len(dct_lst)): #for as long as 'dct_lst' is...
        if dct_lst[i] < min: min = dct_lst[i]; go_to = i
        #look for a number lower than the lowest value. If found then make that new number the new lowest value

    print(f"DICT: {dct} for {min} at {go_to} | {dct_lst}") #testing

    comparison = list(clst.keys()) #make a list out of the keys from 'clst'
    adherence_to = comparison[go_to] #grab the element in the list of keys that shares the index with the lowest number found earlier

    #while True: pass
    #The below sifts through the 'clst' dictionary such that it will find a key value of its own that matches with the one grabbed above
    #For there to be a match the index of the key in 'clst' must equal the index of the lowest value in 'dct_lst'
    #Once a match has been confirmed then the key of 'clst' will add the coordinate of the lowest value to its own set of values
    for key in clst:#for each key in 'clst'...
        if key == adherence_to: #if 'key' is the same value as 'adherence_to'...
            print("TRYING:", key, adherence_to)
            clst[key].append((list(dct.keys())[0], min)) #make 'clst[key]' append the coordinate of the lowest value found from earlier
            #by grabbing the key of the lowest value and inserting it into the position 
            #this is done to find the mean the coords grouped with the mean

    if last_el == True: #The dictionary's key values get jumbled as the iterations go on so this cleans it up
        for key in clst:
            new = []
            for i in range(len(clst[key])):
                if type(clst[key][i][0]) == tuple:
                    new.append(clst[key][i])
            clst[key]=new

    return clst #return refined cluster dict

#The below finds the variance of values in the given list
def find_variance(lst) -> float: #return float
    var_list = []

    for i in range(len(lst)): #for each grouping within the list...
        mean_sum = 0
        for j in range(len(lst[i])):
            mean_sum += lst[i][j]

        mean = mean_sum/len(lst[i]) #Find the mean of this grouping
        print(f"List '{lst[i]}' | Sum: {mean_sum}   Mean: {mean}")
        
        differences = []
        for j in range(len(lst[i])): #find the differences between each value in the grouping and the mean
            differences.append(lst[i][j] - mean)

        print("DIFFERENCE TEST:", differences)

        squared_difference_sum = 0
        for j in range(len(differences)): #square each difference and add them together
            differences[j] = pow(differences[j], 2)
            squared_difference_sum += differences[j]
        print("SQUARED TEST:", squared_difference_sum)
        
        #append the cluster variances to the list
        var_list.append(squared_difference_sum/len(lst[i])) #find the mean of this new sum and append it to the variance list
        #repeat for all groupings

    print("VARIANCE LIST TEST:", var_list)
    variance = 0
    for i in range(len(var_list)): #find the sum of each variance per grouping to achieve the group variance
        variance += var_list[i]
    variance = round(variance, 2) #round the variance to two decimal points if needed

    print("VARIANCE FOR THIS CLUSTER:", variance)
    return variance #return the variance score for iteration

def update_color_set(lst, clrs): return {lst[i]:clrs[i] for i in range(len(lst))}

#Ask the user for the amount of repetitions they want the program to undergo
iter_num = int(input("How many times do you want the program to iterate? "))

#initialize pygame
pygame.init()
width = 1100; height = 640 #set screen width and height
screen = pygame.display.set_mode((width, height)) #make the screen by the bounds of the chosen width and height
clock = pygame.time.Clock() #initiate the clock

def k_means(iter_num):
    global coords_list

    #Variable Setup
    variance_list = [] #For the groupings of euclidean distances per mean generated
    count = 0 #Keeps track of how many iterations the program has gone through, used to stop program when desired repetitions have been met
    restart = False #resets platform after that iteration's cluster has been finalized
    finalized_clusters = {} #stores the finalized clusters generated once per iteration
    positions = [generate_pos(width, height) for _ in range(100)] #generate the position of the data points and store in a list
    finished = False #dictates whether or not the program is finished
    clusters = {} #will house the clusters and their corresponding data points
    final_means = [] #houses the means for the chosen cluster set
    inner_count = 0 #used to break up two process that can likely be grouped together | may remove
    like = 0 #will be used to validate chosen cluster
    mean_colors = ["blue", "red", "mediumspringgreen", "pink", "yellow", "gray", "black", "purple", "orange", "brown", "sky blue", "green"]
    just_started = True

    while True:
        if like == 2:
            count = 0
            iter_num = int(input("How many times do you want the program to iterate? "))
            like = 0; restart = True; finished = False
            finalized_clusters = {}; inner_count = 0

        if count == 0 or restart == True: #sets the program up if a restart is ensued (or if the program just started)
            if count == iter_num: #the count has met the desired amount of iterations...
                if inner_count == 0:
                    print("ALL DONE!")
                    print("LAST CLUSTER:", clusters)
                    finished = True #declare finished
                    inner_count +=1

            else: #if the count hasn't met the desired amount of iterations
                cluster_amount = None
                while cluster_amount == None or 0: #find amount of clusters based on how many data points there are
                    cluster_amount = round(r.randrange(1, len(positions)) * 0.12) 
                means = [generate_pos(width, height) for _ in range(cluster_amount)] #generate list full of means w/ size of cluster amount

                print(f"CLUSTER AMOUNT: {len(means)}")
                clusters = {means[i]:[] for i in range(len(means))} #make dict full of cluster means
                print(f"Initial Clusters: {clusters}")

                #'cluster_comparison_set' will be used to see if there was a change between iterations
                nodes_decisions, cluster_comparison_set = [], []
                #'node_decisions' groups data points and their corresponding distances from each cluster center

                #'count' add onto the count of current iters: will stop when it equates to the desired iter amount
                #'restart' constitutes whether or not the iteration process restarts: will stop on the same condition as 'count'
                count += 1; restart = False

            if finished == True: #if the iteration process is complete...
                if inner_count == 1:
                    sum = 0
                    key_list = list(finalized_clusters.keys()) #make a list out of the finalized cluster's keys
                    for key in key_list:
                        sum += key
                    mean = sum/len(finalized_clusters) #find the mean of keys (the mean of the variance scores)

                    absv_list = []
                    for key in key_list: #get the absolute value of the difference of each variance and the mean
                        absv_list.append(m.fabs(key-mean))

                    min = absv_list[0]
                    for val in absv_list: #get the value with the smallest distance, the one closest to the mean
                        if val < min: min = val
                    
                    smallest = absv_list.index(min) #get the index of the smallest value
                    print(f"ABSOLUTE VARIANCE VALUES: {absv_list} for {smallest} for mean '{mean}'")

                    #get the element corresponding to the smallest value in a list of values
                    wrapped_smallest_abs = list(finalized_clusters.values())[smallest]
                    final_means = list(wrapped_smallest_abs.keys()) #get the value of the keys from the above list
                    breh = list(wrapped_smallest_abs.values())
                    cluster = {list(finalized_clusters.keys())[smallest]:final_means} 
                    #'cluster' is a dict consisted of the above keys and their corresponding variance scores
                    print("CHOSEN CLUSTER:", cluster)#; time.sleep(10)
                    inner_count +=1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        screen.fill('white') #make the background of the window black
        
        if just_started == False:
            for i in range(len(clusters)): #set means of K/cluster centers up on the graph

                clust = []
                if finished == False:
                    clust = list(clusters.keys())
                else:
                    clust = final_means
                
                for j in range(len(positions)):
                    #euclidean distance: sqrt((x2-x1)^2 + (y2-y1)^2)
                    euc_dist = m.sqrt(pow((clust[i][1] - positions[j][1]), 2) + pow((clust[i][0] - positions[j][0]), 2))
                    print(f"Mean '{clust[i]}': {positions[j]} | Distance: {euc_dist}")
                    #euclidean distance is the distance between two data points

                    '''
                    What will the below do?
                    the below will group the position with its euc distances from the mean
                    '''
                    len_nodes = len(nodes_decisions)
                    if len_nodes != len(positions): #if the length of nodes isn't the same how many positions have been set up...
                        nodes_decisions.append({positions[j]:[euc_dist]}) 
                        #add data point and its distance from cluster center to list if not already there
                    if len_nodes == 100:
                        for key in nodes_decisions[j]: #add distance from cluster center to data point to the index of the data center within the dict
                            nodes_decisions[j][key].append(euc_dist)
                            
            
            print(nodes_decisions)
            print(f"NODE DECISIONS: {len(nodes_decisions)} vs {len(positions)} for {cluster_amount} clusters")
            for k in range(len(nodes_decisions)): #for as long as there're elements within 'node_decisions'...
                #for key in nodes_decisions[k]: #for each key value within the element of the list (this element is a dict)...
                if k != 99:
                    clusters=find_min(nodes_decisions[k], clusters) #'find_min' assigns each data_point to the cluster center they're closest to
                else: clusters=find_min(nodes_decisions[k], clusters, True)
                #a more detailed description of 'find_min' can be found above in its initialization
                #The inside of 'nodes_decisions[k] resembles the below:
                #{(r.randint(0,300), r.randint(0,300)):[r.randint(-25, 50) for _ in range(cluster_amount)]}
            print(f"CURRENT CLUSTERS: {clusters} for CLUST: {clust}")
            #time.sleep(10)


            nodes_decisions.clear() #clear the nodes list for the next iter
            clusters = find_mean(clusters) #'find_mean' finds the means of each data point per cluster center
            new_clust = list(clusters.keys()) 
            mean_color_set = update_color_set(new_clust, mean_colors)
            print(f"NEW CLUSTERS: {clusters} for NEW CLUST: {clust}")
            cluster_comparison_set.append(new_clust) #add the list of keys from the new cluster to be compared later
            #time.sleep(10)

            for i in range(len(clusters)): #set means of K/cluster centers up on the graph
                clust = []
                if finished == False:
                    clust = list(clusters.keys())
                else:
                    clust = final_means
                    
                for key in clusters:
                    for i in range(len(clust)):
                        if key == clust[i]:
                            values = clusters[key]
                            color = mean_color_set.get(key)
                            for i in range(len(values)):
                                pygame.draw.circle(screen, color, values[i], 10)
                                pygame.draw.line(screen, color, values[i], key, width=3)

            if len(cluster_comparison_set) == 2: #If there are two values with the comparison set...
                print(f"COMPARING: {cluster_comparison_set[0]} for {cluster_comparison_set[1]}")
                if cluster_comparison_set[0] == cluster_comparison_set[1]: #If these values match...
                    print("CLUSTER WILL BE OBSERVED")
                    print(f"MATCH FOUND: {cluster_comparison_set[0]} for {cluster_comparison_set[1]} at length {len(cluster_comparison_set[1])}")
                    
                    print("VARIANCE LIST:") #iterate through the variance list
                    #The variance list holds the groupings of distances for data points per their cluster center
                    for l in range(len(variance_list)): print(f"{l+1}) {variance_list[l]}")

                    #'find_variance' finds the variance of the solidified cluster (the one that didn't change over a span of 2 iterations)
                    finalized_clusters[find_variance(variance_list)] = clusters #adds this cluster and its variance value to a dict
                    #a more detailed description of 'find_variance' can be found at its initialization
                    print("ALL CLUSTERS:"); counter = 1
                    for key in finalized_clusters:
                        print(f"{counter}) {key}: {finalized_clusters[key]}")
                        counter += 1                

                    restart = True #restart the process
                else: cluster_comparison_set.remove(cluster_comparison_set[0]); print("CHANGING POSITION!")
                #^if there's no match then remove the older element

        else:
            for i in range(len(positions)):
                pygame.draw.circle(screen, "purple", positions[i], 10)

        #update the screen
        pygame.display.update(); clock.tick(60)
        if just_started == True: time.sleep(7); just_started = False

        if finished == True and like == 0: #if you're done and you haven't been asked already...
            like = int(input("Do you like your cluster? Yes(1) No(2): "))

            if like == 1: break
k_means(iter_num)