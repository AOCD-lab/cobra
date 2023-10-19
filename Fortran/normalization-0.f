       subroutine normalization0(Experiments, Electronic, Vb, 
     +            Exp_AV, Exp_SD, Ele_AV, Ele_SD, Vb_AV, Vb_SD,
     +            nSystem, nSteric, nElectronics, nPoints)

      IMPLICIT NONE

      Integer nSystem                        ! # of systems
      Integer nSteric                        ! # of steric parameters
      Integer nElectronics                   ! # of electronic parameters
      Integer nPoints                        ! # of points in the steric grid

      Real*8  Experiments(NSystem)                ! experimental values
      Real*8  Electronic(nSystem,nElectronics)    ! Electronic Parameters
      Real*8  Vb(nSystem, nPoints,nSteric)        ! % buried volume descriptors
      Real*8  Ele_AV(nSystem)                     ! Experimental average
      Real*8  Ele_SD(nSystem)                     ! Experimental standard deviation
      Real*8  Vb_AV(npoints,nSteric)              ! Experimental average
      Real*8  Vb_SD(npoints,nSteric)              ! Experimental standard deviation

      Real*8  Exp_AV         ! Experimental average
      Real*8  Exp_SD         ! Experimental standard deviation

!=========================================================================
! local variables
!=========================================================================
      Integer i, j, k, l

!=========================================================================
! No normalization 
!=========================================================================
      call dnormal2(Experiments(1:nSystem),nSystem,0,Exp_AV,Exp_SD)   
         
      do i = 1, nElectronics
         call dnormal2(Electronic(1:nSystem, i),nSystem,0, 
     +                 Ele_AV(i),Ele_SD(i))
      enddo
      do i = 1, nPoints
         do j = 1, nSteric
            call dnormal2(Vb(1:nSystem, i, j),nSystem,0, 
     x                    Vb_AV(i, j),Vb_SD(i, j))
         enddo
      enddo

      return
      end
