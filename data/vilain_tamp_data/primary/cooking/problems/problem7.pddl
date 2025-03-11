(define (problem cooking)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        cucumber potato - PhysicalObject
        knife - Tool
        cutting_board bowl tray plate knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject cucumber)
        (PhysicalObject potato)
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
        (CanNotReach b_bot cucumber)
        (CanNotReach b_bot potato)

        (At knife knife_holder)
        (At cucumber tray)
        (At potato tray)
    )

    (:goal
        (and
            (Served cucumber bowl)
            (Served potato bowl)
            (isSliced cucumber)
            (isSliced potato)
        )
    )
)
