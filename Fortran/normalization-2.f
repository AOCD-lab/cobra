       subroutine normalization2(Experiments, Electronic, Vb, 
     +            Exp_AV, Exp_SD, Ele_AV, Ele_SD, Vb_AV, Vb_SD,
     +            nSystem, nSteric, nElectronics, nPoints, iSkip)

      IMPLICIT NONE

      Integer nSystem                        ! # of systems
      Integer nSteric                        ! # of steric parameters
      Integer nElectronics                   ! # of electronic parameters
      Integer nPoints                        ! # of points in the steric grid

      Integer iSkip(nSystem)                 ! index of systems to be skipped


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
      Integer i, j, k, l, m, n
      Real*8, Allocatable :: temp(:)     ! experimental values
      Allocate (temp(NSystem))
!=========================================================================
! Normalization of data not skipped
! Start with experimental data
!=========================================================================
      l = 0
      do i = 1,NSystem
         if(iSkip(i).eq.0) then
            l = l + 1
            temp(l) = Experiments(i)
         endif
      enddo
      call dnormal(temp(1:l),l,0,Exp_AV,Exp_SD)   ! normalize experimental value
      l = 0
      do i = 1,NSystem
         if(iSkip(i).eq.0) then
            l = l + 1
            Experiments(i) = temp(l)
         else
            Experiments(i) = (Experiments(i) - Exp_AV)/Exp_SD
         endif
      enddo

!=========================================================================
! Now electronic descriptors
!=========================================================================
      do i = 1, nElectronics
         l = 0
         do j = 1,NSystem
            if(iSkip(j).eq.0) then
               l = l + 1
               temp(l) = Electronic(j,i)
            endif
         enddo
         call dnormal(temp(1:l),l,0,Ele_AV(i),Ele_SD(i))   ! normalize electronic
         l = 0
         do j = 1,NSystem
            if(iSkip(j).eq.0) then
               l = l + 1
               Electronic(j,i) = temp(l)
            else
               Electronic(j,i) = (Electronic(j,i) - Ele_AV(i))/Ele_SD(i)
            endif
         enddo
       enddo

!=========================================================================
! Now steric descriptors
!=========================================================================
      do n = 1, nPoints
         do i = 1, nSteric
            l = 0
            do j = 1,NSystem
               if(iSkip(j).eq.0) then
                  l = l + 1
                  temp(l) = Vb(j,n,i) 
               endif
            enddo
            call dnormal(temp(1:l),l,0,Vb_AV(n,i),Vb_SD(n,i))   ! normalize steric
            l = 0
            do j = 1,NSystem
               if(iSkip(j).eq.0) then
                  l = l + 1
                  Vb(j,n,i) = temp(l)
               else
                  Vb(j,n,i) = (Vb(j,n,i) - Vb_AV(n,i))/Vb_SD(n,i)
               endif
            enddo
         enddo
      enddo

      return
      end
