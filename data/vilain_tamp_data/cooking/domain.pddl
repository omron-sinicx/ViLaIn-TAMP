;Header and description

(define (domain cooking)

    ;remove requirements that are not needed
    (:requirements :strips :equality)

    (:predicates
        ; Static predicates

        ; Type predicates
        (Robot ?x) ; This is predicate is used to declare that something is a robot
        (PhysicalObject ?x) ; This predicate is used to declare that something is a physical object, like a vegetable or fruit
        (Tool ?x) ; This predicate is used to declare that something is a tool (e.g., knife)
        (Location ?x) ; This predicate is used to declare that something is a location (e.g., tray, cutting_board)
        (ToolHolder ?x) ; This predicate is used to declare that a location is a tool holder (e.g., knife holder)

        (isWorkspace ?loc) ; This predicate is used to declare that a location is a workspace (e.g., in cooking, the workspace is the cutting board)
        (Registered ?robot ?obj); This predicate is used as an effect of the "scan" action and can only be True if the scan action is executed

        (HandEmpty ?robot) ; This predicate is used to declare that a robot's hand is empty and not grasping anything
        (Equipped ?robot ?tool) ; This predicated is used when a robot is equipped with a tool, such as a knife

        (CanNotReach ?robot ?obj) ; This predicate is used to declare if the robot is unable to reach an object due to collisions or motion failures (e.g., a_bot cannot reach the ball at the plate)

        ; Goal related predicates
        (Grasping ?robot ?obj) ; This predicate is used to declare that a robot is currently grasping an object

        ; Object state
        (isFixtured ?obj) ; This predicate is used to declare that an object is held down (fixtured). It is the effect of the "fixture" action
        (isSliced ?obj) ; This predicate is used to declare that an object has been sliced. It is the effect of the "slice" action

        (At ?obj ?loc) ; This predicate is used to declare that an object is at a specific location

        (Served ?obj ?loc) ; This predicate is used to declare that an object has been served at a specific location

        (isNotFree ?loc) ; This predicate is used to declare that a location is not free and occupied by an object
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
            (not (At ?obj ?loc))
            (not (isNotFree ?loc))
        )
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
            (not (isNotFree ?loc))
        )
        :effect (and
            (At ?obj ?loc)
            (not (Grasping ?robot ?obj))
            (HandEmpty ?robot)
            (not (Registered ?robot ?obj))
            (isNotFree ?loc)
        )
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
            (isNotFree ?loc)
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
        :parameters (?robot ?obj ?loc1 ?loc2)
        :precondition (and
            (Robot ?robot)
            (PhysicalObject ?obj)
            (Location ?loc1)
            (isWorkspace ?loc1)
            (Location ?loc2)
            (isSliced ?obj)
            (not (isFixtured ?obj))
            (HandEmpty ?robot)
            (not (CanNotReach ?robot ?obj))
        )
        :effect (and
            (Served ?obj ?loc2)
            (not (At ?obj ?loc1))
            (not (isNotFree ?loc1))
        )
    )

)
