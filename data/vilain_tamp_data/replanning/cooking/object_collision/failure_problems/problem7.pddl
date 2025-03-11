(define (problem pick_and_place)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        potato carrot - PhysicalObject
        knife - Tool
        cutting_board tray plate knife_holder - Location
    )

    (:init
        (Robot a_bot)
        (Robot b_bot)
        (PhysicalObject potato)
        (PhysicalObject carrot)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)

        (At knife knife_holder)
        (At potato tray)
        (At carrot cutting_board)
    )

    (:goal
        (and
            (At potato cutting_board)
        )
    )
)
