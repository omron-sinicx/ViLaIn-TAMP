(define (problem pick_and_place)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        tomato carrot - PhysicalObject
        knife - Tool
        cutting_board tray plate knife_holder other_plate - Location
    )

    (:init
        (Robot a_bot)
        (PhysicalObject tomato)
        (PhysicalObject carrot)
        (Tool knife)

        (HandEmpty a_bot)

        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location knife_holder)
        (Location other_plate)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)

        (At knife knife_holder)
        (At tomato tray)
        (At carrot cutting_board)
    )

    (:goal
        (and
            (At tomato cutting_board)
        )
    )
)
