(define (problem cooking)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        cucumber - PhysicalObject
        knife - Tool
        cutting_board bowl tray knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject cucumber)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)
        (CanNotReach b_bot cucumber)

        (At knife knife_holder)
        (At cucumber tray)
    )

    (:goal
        (and
            (Served cucumber bowl)
            (isSliced cucumber)
        )
    )
)
