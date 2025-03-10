(define (problem cooking)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        cucumber potato carrot - PhysicalObject
        knife - Tool
        cutting_board bowl tray plate knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject cucumber)
        (PhysicalObject potato)
        (PhysicalObject carrot)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)
        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location knife_holder)
        (Location other_plate)
        (ToolHolder knife_holder)
        (isWorkspace cutting_board)
        (CanNotReach b_bot cucumber)
        (CanNotReach b_bot potato)
        (CanNotReach b_bot carrot)
        (At knife knife_holder)
        (At cucumber tray)
        (At potato tray)
        (At carrot tray)
    )

    (:goal
        (and
            (Served cucumber bowl)
            (Served potato bowl)
            (Served carrot bowl)
            (isSliced cucumber)
            (isSliced potato)
            (isSliced carrot)
        )
    )
)
