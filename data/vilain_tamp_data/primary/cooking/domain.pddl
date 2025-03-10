;Header and description

(define (domain cooking)

    ;remove requirements that are not needed
    (:requirements :strips :equality)

    (:predicates
        ; Static predicates

        ; Type predicates
        (Robot ?x) ; true if x is a robot
        (PhysicalObject ?x) ; true if x is a physical object (e.g., cucumber, tomato)
        (Tool ?x) ; true if x is a tool (e.g., knife)
        (Location ?x) ; true if x is a location (e.g., tray, cutting_board)
        (ToolHolder ?x) ; true if x is a tool holder (e.g., knife holder)

        (isWorkspace ?loc) ; Is the location a workspace? (In this context, workspace refers to the location to slice = cutting_board)
        (Registered ?robot ?obj); The actual location and pose of the object is KNOWN

        ; Robot state predicates
        (HandEmpty ?robot) ; Is the robot hand free?
        (Equipped ?robot ?tool) ; Is the robot equipped with a tool (e.g., knife)?

        ;Robot motion constraints
        (CanNotReach ?robot ?obj) ; Can the robot reach the object? (True if robot cannot)

        ; Goal related predicates
        (Grasping ?robot ?obj) ; Is the robot grasping an object?

        ; Object state
        (isFixtured ?obj) ; Is the object held down (fixtured)?
        (isSliced ?obj) ; Is the cucumber sliced or whole?

        (At ?obj ?loc) ; Is the object at a specific location (e.g., tray, cutting_board)

        (Served ?obj ?loc) ; Is the object served at a location?
        (Reoriented ?obj ?loc) ; Has the object pose been reoriented to the correct pose?
    )

    ; SCAN: Look for objects in the tray
    (:action scan
        :parameters (?robot ?obj ?loc)
        :precondition (and
            (Robot ?robot)
            (PhysicalObject ?obj)
            (Location ?loc)
            (HandEmpty ?robot)
            (At ?obj ?loc)
            (not (Registered ?robot ?obj))
        )
        :effect (and
            (Registered ?robot ?obj)
        )
    )

    ; PICK: Pick up an object
    (:action pick
        :parameters (?robot ?obj ?loc)
        :precondition (and
            (Robot ?robot)
            (PhysicalObject ?obj)
            (Location ?loc)
            (Registered ?robot ?obj)
            (not (CanNotReach ?robot ?obj))
            (At ?obj ?loc)
            (HandEmpty ?robot)
        )
        :effect (and
            (Grasping ?robot ?obj)
            (not (HandEmpty ?robot))
            (not (At ?obj ?loc)))
    )

    ; PLACE: Place an object
    (:action place
        :parameters (?robot ?obj ?loc)
        :precondition (and
            (Robot ?robot)
            (PhysicalObject ?obj)
            (Location ?loc)
            (Grasping ?robot ?obj)
            (not (HandEmpty ?robot))
            (not (At ?obj ?loc))
            (not (CanNotReach ?robot ?obj))
        )
        :effect (and
            (At ?obj ?loc)
            (not (Grasping ?robot ?obj))
            (HandEmpty ?robot)
            (not (Registered ?robot ?obj))
        )
    )

    ; REORIENT: Reorient the position of an object using pick-and-place
    (:action reorient
        :parameters (?robot ?obj ?loc)
        :precondition (and
            (Robot ?robot)
            (PhysicalObject ?obj)
            (Registered ?robot ?obj)
            (Location ?loc)
            (HandEmpty ?robot)
            (not (Grasping ?robot ?obj))
            (not (CanNotReach ?robot ?obj))
            (not (Reoriented ?obj ?loc))
            (At ?obj ?loc)
        )
        :effect (and
            (Reoriented ?obj ?loc))
    )

    ; EQUIP_TOOL: Pick up a tool
    (:action equip_tool
        :parameters (?robot ?tool ?loc ?obj)
        :precondition (and
            (Robot ?robot)
            (Tool ?tool)
            (isFixtured ?obj)
            (HandEmpty ?robot)
            (ToolHolder ?loc)
            (At ?tool ?loc)
            (not (CanNotReach ?robot ?tool))
        )
        :effect (and
            (Equipped ?robot ?tool)
            (not (HandEmpty ?robot))
            (not (At ?tool ?loc))
        )
    )

    ; FIXTURE: Hold down (fixture) the object on the workspace using a robot arm before slicing
    (:action fixture
        :parameters (?robot ?obj ?loc)
        :precondition (and
            (Robot ?robot)
            (PhysicalObject ?obj)
            (At ?obj ?loc)
            (HandEmpty ?robot)
            (not (CanNotReach ?robot ?obj))
            (isWorkspace ?loc)
        )
        :effect (and
            (not (HandEmpty ?robot))
            (isFixtured ?obj)
        )
    )

    ; SLICE: Slice an object
    (:action slice
        :parameters (?robot ?tool ?obj ?loc)
        :precondition (and
            (Robot ?robot)
            (Tool ?tool)
            (Location ?loc)
            (PhysicalObject ?obj)
            (Equipped ?robot ?tool)
            (isFixtured ?obj)
            (isWorkspace ?loc)
            (At ?obj ?loc)
        )
        :effect (and
            (isSliced ?obj)
            (not (Registered ?robot ?obj))
        )
    )

    ; UNEQUIP_TOOL: Place down & return a tool
    (:action unequip_tool
        :parameters (?robot ?tool ?loc)
        :precondition (and
            (Robot ?robot)
            (Tool ?tool)
            (ToolHolder ?loc)
            (Equipped ?robot ?tool)
        )
        :effect (and
            (not (Equipped ?robot ?tool))
            (At ?tool ?loc)
            (HandEmpty ?robot)
        )
    )

    ; CLEAN_UP: Subroutine of returning leftover cucumber
    (:action clean_up
        :parameters (?robot ?obj)
        :precondition (and
            (Robot ?robot)
            (PhysicalObject ?obj)
            (isSliced ?obj)
        )
        :effect (and
            (not (isFixtured ?obj))
            (HandEmpty ?robot)
        )
    )

    ;SERVE_FOOD: Repeated pick-and-place actions for serving slices onto a location (e.g., plate)
    (:action serve_food
        :parameters (?robot ?obj ?loc)
        :precondition (and
            (Robot ?robot)
            (PhysicalObject ?obj)
            (Location ?loc)
            (isSliced ?obj)
            (not (isFixtured ?obj))
            (HandEmpty ?robot)
            (not (CanNotReach ?robot ?obj))
        )
        :effect (and
            (Served ?obj ?loc)
        )
    )

)
