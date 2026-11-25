import time
from students_data import STUDENT_1_BY_SIZE, STUDENT_2_BY_SIZE
#Gets the student data from the students_data.py file and assigns it to variables for use in the matching algorithms.(20-80 by tens)
students_1 = STUDENT_1_BY_SIZE[80]
student_2 = STUDENT_2_BY_SIZE[80]

def stable_match(students_1, student_2):
    """ This function takes in the students data and 
    returns a stable matching of students to student. """
    room_cap = 1

    # Dictionary to hold the matches
    matches = {student: [] for student in student_2}
    # Dictionary to hold the number of attempts made by each student to match with a student
    attempted_match = {student: 0 for student in students_1}
    no_match = set()
    # Dictionary to hold the rank of each student in the preference list of each student
    room_rank = {room: {student: rank for rank, student in enumerate(pref)}
        for room, pref in student_2.items()}

    # Matches students to students based on their preferences of each other and the capacity of each student. 
    # If a student has already been matched to a student, they will not be matched again. 
    # If a student has no more preferences left to match with, they will be added to the no_match set and will not be matched again.
    while any(student not in no_match and
              student not in [s for room in matches.values() for s in room]
              for student in students_1):
        pref = next(student for student in students_1
            if student not in no_match and student not in [s for room in matches.values() for s in room])
        if attempted_match[pref] >= len(students_1[pref]):
            no_match.add(pref)
            continue
        act = students_1[pref][attempted_match[pref]]
        attempted_match[pref] += 1
        if act not in matches or pref not in room_rank[act]:
            continue
        if len(matches[act]) < room_cap:
            matches[act].append(pref)
        else:
            current_s = max(matches[act],key=lambda s: room_rank[act][s])
            if room_rank[act][pref] < room_rank[act][current_s]:
                matches[act].remove(current_s)
                matches[act].append(pref)
    # Create a dictionary of the matches where each student is matched to their assigned student
    s_matches = {}
    for room, room_students in matches.items():
        for student in room_students:
            s_matches[student] = room
    #Return the dictionary of matches
    return s_matches

def maximum_weight_bipartite_matching(students_1, student_2):
    """ This function takes in the student data and 
    returns matches from students_1 IDs to student_2 IDs. """
    left = list(student_2)
    right = list(students_1)
    source = 0
    left_start = 1
    right_start = left_start + len(left)
    sink = right_start + len(right)
    graph = [[] for _ in range(sink + 1)]
    # Add edges to the graph
    def add_edge(start, end, capacity, cost):
        forward = [end, len(graph[end]), capacity, cost]
        reverse = [start, len(graph[start]), 0, -cost]
        graph[start].append(forward)
        graph[end].append(reverse)
        return forward
    # Create a mapping of students to their indices in the graph and add edges from the source to the left students 
    # and from the right students to the sink
    left_index = {student: left_start + i for i, student in enumerate(left)}
    right_index = {student: right_start + i for i, student in enumerate(right)}

    for student in left:
        add_edge(source, left_index[student], 1, 0)
    for student in right:
        add_edge(right_index[student], sink, 1, 0)

    # Create edges between left and right students based on their preferences and weights
    matching_edges = []
    for student, preferences in student_2.items():
        seen = set()
        for rank, room in enumerate(preferences):
            if room in right_index and room not in seen:
                seen.add(room)
                weight = len(preferences) - rank
                edge = add_edge(left_index[student], right_index[room], 1, -weight)
                matching_edges.append((student, room, edge))
    # Use the Bellman-Ford algorithm to find the shortest path from the source to the sink in terms of cost, 
    # and augment the flow along that path until no more augmenting paths can be found
    while True:
        distances = [float("inf")] * len(graph)
        previous = [None] * len(graph)
        distances[source] = 0
        for _ in range(len(graph) - 1):
            changed = False
            for node, edges in enumerate(graph):
                if distances[node] == float("inf"):
                    continue
                for edge_index, edge in enumerate(edges):
                    destination, _, capacity, cost = edge
                    candidate = distances[node] + cost
                    if capacity and candidate < distances[destination]:
                        distances[destination] = candidate
                        previous[destination] = (node, edge_index)
                        changed = True
            if not changed:
                break

        if previous[sink] is None:
            break

        node = sink
        while node != source:
            parent, edge_index = previous[node]
            edge = graph[parent][edge_index]
            edge[2] -= 1
            graph[node][edge[1]][2] += 1
            node = parent
    # Create a dictionary of the matches based on the edges that have been used in the flow
    return {room: student for student, room, edge in matching_edges if edge[2] == 0}

def satisfaction_score(matching, students_1, student_2) -> dict:
    """scores a matching from the student own point of view. 
 matching maps each student_1 to the student_2 they were given. 
A student satisfaction is (L - rank) / L where rank is the position 
of their partner in their own preference list 0 = first choice and L is the length of that list.
 So 1.0 is their top choice and 1/L is their last choice. Unmatched students score 0."""
    # score for one student based on where their partner is in their own list
    def score(prefs, partner):
        if partner is None or partner not in prefs:
            return 0.0
        return (len(prefs) - prefs.index(partner)) / len(prefs)
    #Flip the matching so we can also look up each student_2 partner
    partner_of_2 = {room: student for student, room in matching.items()}
    #A score for every student in each group
    scores_1 = [score(prefs, matching.get(student)) for student, prefs in students_1.items()]
    scores_2 = [score(prefs, partner_of_2.get(student)) for student, prefs in student_2.items()]
    everyone = scores_1 + scores_2
    # Return the satisfaction scores for both groups and overall
    return {
        "students_1": sum(scores_1) / len(scores_1), # average for group 1
        "student_2": sum(scores_2) / len(scores_2), # average for group 2
        "overall": sum(everyone) / len(everyone), # average for everyone
        "worst_off": min(everyone), # least happy student
        "first_choices": sum(1 for s in everyone if s == 1.0), # how many got their first choice
        "matched_pairs": len(matching), # how many pairs were made
    }
    

def print_satisfaction(name, scores) -> None:
    """prints the satisfaction score summary for one algorithm."""
    print(f"{name} satisfaction (1.0 = everyone got their first choice):")
    print(f" Student 1 average: {scores['students_1']:.3f}")
    print(f" Student 2 average: {scores['student_2']:.3f}")
    print(f" Overall average: {scores['overall']:.3f}")
    print(f" Least satisfied student: {scores['worst_off']:.3f}")
    print(f" Students who got their first choice: {scores['first_choices']}")
    print(f" Matched pairs: {scores['matched_pairs']}\n") # \n adds a blank line after


def main(students_1, student_2) -> None:
    """Main function that takes in the student data and runs both the stable matching and maximum-weight bipartite matching algorithms, 
    printing the results and their execution times. """

    # Run the stable matching algorithm and measure its execution time
    start_time = time.perf_counter()
    stable = stable_match(students_1, student_2)
    end_time = time.perf_counter()
    ex_time_1 = end_time-start_time
    # Print the results of the stable matching algorithm
    print("Stable Matching of Students:")
    for student_1 in sorted(students_1):
        match = stable.get(student_1)
        if match is None:
            print(f"Student_1 {student_1}: no match")
        else:
            print(f"Student_1 {student_1} -> Student_2 {match}")
    print("\n")
    # Run the maximum-weight bipartite matching algorithm and measure its execution time
    print("Maximum-weight bipartite matching of Students:")
    start_time = time.perf_counter()
    max_weight = maximum_weight_bipartite_matching(students_1, student_2)
    end_time = time.perf_counter()
    ex_time_2 = end_time-start_time
    # Print the results of the maximum-weight bipartite matching algorithm
    for student_1 in sorted(students_1):
        match = max_weight.get(student_1)
        if match is None:
            print(f"Student_1 {student_1}: no match")
        else:
            print(f"Student_1 {student_1} -> Student_2 {match}")
    print("\n")
    # Print the execution times of both algorithms
    print(f" Stable Matching Runtime: {ex_time_1:.6f} seconds\n")
    print(f" Maximum-weight Bipartite Matching Runtime: {ex_time_2:.6f} seconds\n")
    #satifactory scores for both algorithms
    print_satisfaction("Stable Matching", satisfaction_score(stable, students_1, student_2))
    print_satisfaction("Maximum-weight Bipartite Matching", satisfaction_score(max_weight, students_1, student_2))
if __name__ == "__main__":
	main(students_1, student_2)
         
