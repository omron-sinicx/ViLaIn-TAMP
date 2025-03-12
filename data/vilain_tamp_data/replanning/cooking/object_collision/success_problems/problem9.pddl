(define (problem pick_and_place)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        apple carrot - PhysicalObject
        knife - Tool
        cutting_board tray plate plate2 knife_holder - Location
    )

    (:init
        (Robot a_bot)
        (PhysicalObject apple)
        (PhysicalObject carrot)
        (Tool knife)

        (HandEmpty a_bot)

        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location plate2)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)

        (At knife knife_holder)
        (At apple plate)
        (At carrot plate2)
    )

    (:goal
        (and
            (At apple plate2)
            (not (At carrot plate2))
        )
    )
)
