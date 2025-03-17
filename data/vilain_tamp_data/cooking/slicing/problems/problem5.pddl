(define (problem cooking)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        carrot cucumber - PhysicalObject
        knife - Tool
        cutting_board bowl tray knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject carrot)
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
        (CanNotReach b_bot carrot)
        (CanNotReach b_bot cucumber)

        (At knife knife_holder)
        (At carrot tray)
        (At cucumber tray)
    )

    (:goal
        (and
            (Served carrot bowl)
            (Served cucumber bowl)
            (isSliced carrot)
            (isSliced cucumber)
        )
    )
)
